from abc import ABC, abstractmethod
import asyncio
import logging
from typing import cast, Dict, List, Self

from bs4 import BeautifulSoup
import httpx

from fraudcrawler.settings import (
    PROCESSOR_DEFAULT_MODEL,
)
from fraudcrawler.settings import (
    DEFAULT_N_SERP_WKRS,
    DEFAULT_N_ZYTE_WKRS,
    DEFAULT_N_PROC_WKRS,
)
from fraudcrawler.base.base import (
    Deepness,
    Host,
    Language,
    Location,
    Prompt,
    ProductItem,
    HttpxAsyncClient,
)
from fraudcrawler import (
    Search,
    SearchEngineName,
    Enricher,
    URLCollector,
    ZyteAPI,
    Processor,
)

logger = logging.getLogger(__name__)


class Orchestrator(ABC):
    """Abstract base class for orchestrating the different actors (crawling, processing).

    Abstract methods:
        _collect_results: Collects the results from the given queue_in.

    Each subclass of class:`Orchestrator` must implement the abstract method func:`_collect_results`.
    This function is responsible for collecting and handling the results from the given queue_in. It might
    save the results to a file, a database, or any other storage.

    For each pipeline step class:`Orchestrator` will deploy a number of async workers to handle the tasks.
    In addition it makes sure to orchestrate the canceling of the workers only after the relevant workload is done.

    For more information on the orchestrating pattern see README.md.
    """

    def __init__(
        self,
        serpapi_key: str,
        dataforseo_user: str,
        dataforseo_pwd: str,
        zyteapi_key: str,
        openaiapi_key: str,
        openai_model: str = PROCESSOR_DEFAULT_MODEL,
        n_serp_wkrs: int = DEFAULT_N_SERP_WKRS,
        n_zyte_wkrs: int = DEFAULT_N_ZYTE_WKRS,
        n_proc_wkrs: int = DEFAULT_N_PROC_WKRS,
        # Configure a custom httpx client.
        # We provide a `HttpxAsyncClient` class that you can pass
        # to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        http_client: httpx.AsyncClient | None = None,
    ):
        """Initializes the orchestrator with the given settings.

        NOTE:
        The class:`Orchestrator` must be used as context manager as follows:
            async with Orchestrator(...) as orchestrator:
                await orchestrator.run()

        Args:
            serpapi_key: The API key for SERP API.
            dataforseo_user: The user for DataForSEO.
            dataforseo_pwd: The password for DataForSEO.
            zyteapi_key: The API key for Zyte API.
            openaiapi_key: The API key for OpenAI.
            openai_model: The model to use for the processing (optional).
            n_serp_wkrs: Number of async workers for serp (optional).
            n_zyte_wkrs: Number of async workers for zyte (optional).
            n_proc_wkrs: Number of async workers for the processor (optional).
            http_client: An httpx.AsyncClient to use for the async requests (optional).
        """

        # Store the variables for setting up the clients
        self._serpapi_key = serpapi_key
        self._dataforseo_user = dataforseo_user
        self._dataforseo_pwd = dataforseo_pwd
        self._zyteapi_key = zyteapi_key
        self._openaiapi_key = openaiapi_key
        self._openai_model = openai_model

        # Setup the async framework
        self._n_serp_wkrs = n_serp_wkrs
        self._n_zyte_wkrs = n_zyte_wkrs
        self._n_proc_wkrs = n_proc_wkrs
        self._queues: Dict[str, asyncio.Queue] | None = None
        self._workers: Dict[str, List[asyncio.Task] | asyncio.Task] | None = None

        # Setup the httpx client
        self._http_client = http_client
        self._owns_http_client = http_client is None

    async def __aenter__(self) -> Self:
        """Creates and starts an httpx.AsyncClient if not provided."""
        if self._http_client is None:
            logger.debug("Creating a new httpx.AsyncClient owned by the orchestrator")
            self._http_client = HttpxAsyncClient()
            self._owns_http_client = True

        # Setup the clients
        self._zyteapi = ZyteAPI(
            http_client=self._http_client, api_key=self._zyteapi_key
        )
        self._search = Search(
            http_client=self._http_client,
            serpapi_key=self._serpapi_key,
            zyte_api=self._zyteapi,
        )
        self._enricher = Enricher(
            http_client=self._http_client,
            user=self._dataforseo_user,
            pwd=self._dataforseo_pwd,
        )
        self._url_collector = URLCollector()
        self._processor = Processor(
            http_client=self._http_client,
            api_key=self._openaiapi_key,
            model=self._openai_model,
        )
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """Closes the httpx.AsyncClient if it was created by this orchestrator."""
        if self._owns_http_client and self._http_client is not None:
            logger.debug("Closing the httpx.AsyncClient owned by the orchestrator")
            await self._http_client.aclose()
            self._http_client = None

    async def _serp_execute(
        self,
        queue_in: asyncio.Queue[dict | None],
        queue_out: asyncio.Queue[ProductItem | None],
    ) -> None:
        """Collects the search setups from the queue_in, executes the search, filters the results and puts them into queue_out.

        Args:
            queue_in: The input queue containing the search parameters.
            queue_out: The output queue to put the found urls.
        """
        while True:
            item = await queue_in.get()
            if item is None:
                queue_in.task_done()
                break

            try:
                search_term_type = item.pop("search_term_type")
                # The search_engines are already SearchEngineName enum values
                search_engines = item.pop("search_engines")

                results = await self._search.apply(
                    **item, search_engines=search_engines
                )

                logger.debug(
                    f"Search for {item['search_term']} returned {len(results)} results"
                )
                for res in results:
                    product = ProductItem(
                        search_term=item["search_term"],
                        search_term_type=search_term_type,
                        url=res.url,
                        url_resolved=res.url,  # Set initial value, will be updated by Zyte
                        search_engine_name=res.search_engine_name,
                        domain=res.domain,
                        filtered=res.filtered,
                        filtered_at_stage=res.filtered_at_stage,
                    )
                    await queue_out.put(product)
            except Exception as e:
                logger.error(f"Error executing search: {e}")
            queue_in.task_done()

    async def _collect_url(
        self,
        queue_in: asyncio.Queue[ProductItem | None],
        queue_out: asyncio.Queue[ProductItem | None],
    ) -> None:
        """Collects the URLs from the given queue_in, checks for duplicates, and puts them into the queue_out.

        Args:
            queue_in: The input queue containing the URLs.
            queue_out: The output queue to put the URLs.
        """
        while True:
            product = await queue_in.get()
            if product is None:
                queue_in.task_done()
                break

            if not product.filtered:
                # Clean the URL by removing tracking parameters
                url = self._url_collector.remove_tracking_parameters(product.url)
                product.url = url

                if url in self._url_collector.collected_currently:
                    # deduplicate on current run
                    product.filtered = True
                    product.filtered_at_stage = (
                        "URL collection (current run deduplication)"
                    )
                    logger.debug(f"URL {url} already collected in current run")
                elif url in self._url_collector.collected_previously:
                    # deduplicate on previous runs coming from a db
                    product.filtered = True
                    product.filtered_at_stage = (
                        "URL collection (previous run deduplication)"
                    )
                    logger.debug(f"URL {url} as already collected in previous run")
                else:
                    self._url_collector.collected_currently.add(url)

            await queue_out.put(product)
            queue_in.task_done()

    async def _zyte_execute(
        self,
        queue_in: asyncio.Queue[ProductItem | None],
        queue_out: asyncio.Queue[ProductItem | None],
    ) -> None:
        """Collects the URLs from the queue_in, enriches it with product details metadata, filters them (probability), and puts them into queue_out.

        Args:
            queue_in: The input queue containing URLs to fetch product details from.
            queue_out: The output queue to put the product details as dictionaries.
        """
        while True:
            product = await queue_in.get()
            if product is None:
                queue_in.task_done()
                break

            if not product.filtered:
                try:
                    # Fetch the product details from Zyte API
                    details = await self._zyteapi.details(url=product.url)
                    url_resolved = self._zyteapi.extract_url_resolved(details=details)
                    if url_resolved:
                        product.url_resolved = url_resolved
                    product.product_name = self._zyteapi.extract_product_name(
                        details=details
                    )

                    # If the resolved URL is different from the original URL, we also need to update the domain as
                    # otherwise the unresolved domain will be shown, for example for unresolved domain toppreis.ch but resolved digitec.ch
                    if url_resolved and url_resolved != product.url:
                        logger.debug(
                            f"URL resolved for {product.url} is {url_resolved}"
                        )
                        product.domain = self._search._get_domain(url_resolved)

                    product.product_price = self._zyteapi.extract_product_price(
                        details=details
                    )
                    product.product_description = (
                        self._zyteapi.extract_product_description(details=details)
                    )
                    product.product_images = self._zyteapi.extract_image_urls(
                        details=details
                    )
                    product.probability = self._zyteapi.extract_probability(
                        details=details
                    )
                    product.html = self._zyteapi.extract_html(details=details)
                    if product.html:
                        soup = BeautifulSoup(product.html, "html.parser")
                        product.html_clean = soup.get_text(separator=" ", strip=True)
                    # Filter the product based on the probability threshold
                    if not self._zyteapi.keep_product(details=details):
                        product.filtered = True
                        product.filtered_at_stage = "Zyte probability threshold"
                except Exception as e:
                    logger.warning(f"Error executing Zyte API search: {e}.")
            await queue_out.put(product)
            queue_in.task_done()

    async def _proc_execute(
        self,
        queue_in: asyncio.Queue[ProductItem | None],
        queue_out: asyncio.Queue[ProductItem | None],
        prompts: List[Prompt],
    ) -> None:
        """Collects the product details from the queue_in, processes them (filtering, relevance, etc.) and puts the results into queue_out.

        Args:
            queue_in: The input queue containing the product details.
            queue_out: The output queue to put the processed product details.
            prompts: The list of prompts to use for classification.
        """

        # Process the products
        while True:
            product = await queue_in.get()
            if product is None:
                # End of queue signal
                queue_in.task_done()
                break

            if not product.filtered:
                try:
                    # Run all the configured prompts
                    for prompt in prompts:
                        classification = await self._processor.classify(
                            product=product,
                            prompt=prompt,
                        )
                        product.classifications[prompt.name] = int(
                            classification.result
                        )
                        product.usage[prompt.name] = {
                            "input_tokens": classification.input_tokens,
                            "output_tokens": classification.output_tokens,
                        }
                except Exception as e:
                    logger.warning(
                        f"Error processing product with url={product.url}: {e}."
                    )

            await queue_out.put(product)
            queue_in.task_done()

    @abstractmethod
    async def _collect_results(
        self, queue_in: asyncio.Queue[ProductItem | None]
    ) -> None:
        """Collects the results from the given queue_in.

        Args:
            queue_in: The input queue containing the results.
        """
        pass

    def _setup_async_framework(
        self,
        n_serp_wkrs: int,
        n_zyte_wkrs: int,
        n_proc_wkrs: int,
        prompts: List[Prompt],
    ) -> None:
        """Sets up the necessary queues and workers for the async framework.

        Args:
            n_serp_wkrs: Number of async workers for serp.
            n_zyte_wkrs: Number of async workers for zyte.
            n_proc_wkrs: Number of async workers for processor.
            prompts: The list of prompts used for the classification by func:`Processor.classify`.
        """

        # Setup the input/output queues for the workers
        serp_queue: asyncio.Queue[dict | None] = asyncio.Queue()
        url_queue: asyncio.Queue[ProductItem | None] = asyncio.Queue()
        zyte_queue: asyncio.Queue[ProductItem | None] = asyncio.Queue()
        proc_queue: asyncio.Queue[ProductItem | None] = asyncio.Queue()
        res_queue: asyncio.Queue[ProductItem | None] = asyncio.Queue()

        # Setup the Serp workers
        serp_wkrs = [
            asyncio.create_task(
                self._serp_execute(
                    queue_in=serp_queue,
                    queue_out=url_queue,
                )
            )
            for _ in range(n_serp_wkrs)
        ]

        # Setup the URL collector
        url_col = asyncio.create_task(
            self._collect_url(queue_in=url_queue, queue_out=zyte_queue)
        )

        # Setup the Zyte workers
        zyte_wkrs = [
            asyncio.create_task(
                self._zyte_execute(
                    queue_in=zyte_queue,
                    queue_out=proc_queue,
                )
            )
            for _ in range(n_zyte_wkrs)
        ]

        # Setup the processing workers
        proc_wkrs = [
            asyncio.create_task(
                self._proc_execute(
                    queue_in=proc_queue,
                    queue_out=res_queue,
                    prompts=prompts,
                )
            )
            for _ in range(n_proc_wkrs)
        ]

        # Setup the result collector
        res_col = asyncio.create_task(self._collect_results(queue_in=res_queue))

        # Add the setup to the instance variables
        self._queues = {
            "serp": serp_queue,
            "url": url_queue,
            "zyte": zyte_queue,
            "proc": proc_queue,
            "res": res_queue,
        }
        self._workers = {
            "serp": serp_wkrs,
            "url": url_col,
            "zyte": zyte_wkrs,
            "proc": proc_wkrs,
            "res": res_col,
        }

    @staticmethod
    async def _add_serp_items_for_search_term(
        queue: asyncio.Queue[dict | None],
        search_term: str,
        search_term_type: str,
        search_engines: List[SearchEngineName],
        language: Language,
        location: Location,
        num_results: int,
        marketplaces: List[Host] | None,
        excluded_urls: List[Host] | None,
    ) -> None:
        """Adds a search-item to the queue."""
        item = {
            "search_term": search_term,
            "search_term_type": search_term_type,
            "search_engines": search_engines,
            "language": language,
            "location": location,
            "num_results": num_results,
            "marketplaces": marketplaces,
            "excluded_urls": excluded_urls,
        }
        logger.debug(f'Adding item="{item}" to serp_queue')
        await queue.put(item)

    async def _add_serp_items(
        self,
        queue: asyncio.Queue[dict | None],
        search_term: str,
        search_engines: List[SearchEngineName],
        language: Language,
        location: Location,
        deepness: Deepness,
        marketplaces: List[Host] | None,
        excluded_urls: List[Host] | None,
    ) -> None:
        """Adds all the (enriched) search_term (as serp items) to the queue."""
        common_kwargs = {
            "queue": queue,
            "language": language,
            "location": location,
            "marketplaces": marketplaces,
            "excluded_urls": excluded_urls,
        }

        # Add initial items to the serp_queue
        await self._add_serp_items_for_search_term(
            search_term=search_term,
            search_term_type="initial",
            search_engines=search_engines,
            num_results=deepness.num_results,
            **common_kwargs,  # type: ignore[arg-type]
        )

        # Enrich the search_terms
        enrichment = deepness.enrichment
        if enrichment:
            # Call DataForSEO to get additional terms
            n_terms = enrichment.additional_terms
            terms = await self._enricher.enrich(
                search_term=search_term,
                language=language,
                location=location,
                n_terms=n_terms,
            )

            # Add the enriched search terms to the serp_queue
            for trm in terms:
                await self._add_serp_items_for_search_term(
                    search_term=trm,
                    search_term_type="enriched",
                    search_engines=search_engines,
                    num_results=enrichment.additional_urls_per_term,
                    **common_kwargs,  # type: ignore[arg-type]
                )

    async def run(
        self,
        search_term: str,
        search_engines: List[SearchEngineName],
        language: Language,
        location: Location,
        deepness: Deepness,
        prompts: List[Prompt],
        marketplaces: List[Host] | None = None,
        excluded_urls: List[Host] | None = None,
        previously_collected_urls: List[str] | None = None,
    ) -> None:
        """Runs the pipeline steps: serp, enrich, zyte, process, and collect the results.

        Args:
            search_term: The search term for the query.
            search_engines: The list of search engines to use for the search query.
            language: The language to use for the query.
            location: The location to use for the query.
            deepness: The search depth and enrichment details.
            prompts: The list of prompt to use for classification.
            marketplaces: The marketplaces to include in the search.
            excluded_urls: The URLs to exclude from the search.
            previously_collected_urls: The urls that have been collected previously and are ignored.
        """
        # ---------------------------
        #        INITIAL SETUP
        # ---------------------------
        # Ensure we have at least one search engine
        if not search_engines:
            logger.warning(
                "No search engines specified, using all available search engines"
            )
            search_engines = list(SearchEngineName)

        # Handle previously collected URLs
        if previously_collected_urls:
            self._url_collector.collected_previously = set(previously_collected_urls)

        # Setup the async framework
        n_terms_max = 1 + (
            deepness.enrichment.additional_terms if deepness.enrichment else 0
        )
        n_serp_wkrs = min(self._n_serp_wkrs, n_terms_max)
        n_zyte_wkrs = min(self._n_zyte_wkrs, deepness.num_results)
        n_proc_wkrs = min(self._n_proc_wkrs, deepness.num_results)

        logger.debug(
            f"setting up async framework (#workers: serp={n_serp_wkrs}, zyte={n_zyte_wkrs}, proc={n_proc_wkrs})"
        )
        self._setup_async_framework(
            n_serp_wkrs=n_serp_wkrs,
            n_zyte_wkrs=n_zyte_wkrs,
            n_proc_wkrs=n_proc_wkrs,
            prompts=prompts,
        )

        # Check setup of async framework
        if self._queues is None or self._workers is None:
            raise ValueError(
                "Async framework is not setup. Please call _setup_async_framework() first."
            )
        if not all([k in self._queues for k in ["serp", "url", "zyte", "proc", "res"]]):
            raise ValueError(
                "The queues of the async framework are not setup correctly."
            )
        if not all(
            [k in self._workers for k in ["serp", "url", "zyte", "proc", "res"]]
        ):
            raise ValueError(
                "The workers of the async framework are not setup correctly."
            )

        # Add the search items to the serp_queue
        serp_queue = self._queues["serp"]
        await self._add_serp_items(
            queue=serp_queue,
            search_term=search_term,
            search_engines=search_engines,
            language=language,
            location=location,
            deepness=deepness,
            marketplaces=marketplaces,
            excluded_urls=excluded_urls,
        )

        # ---------------------------
        #   ORCHESTRATE SERP WORKERS
        # ---------------------------
        # Add the sentinels to the serp_queue
        for _ in range(n_serp_wkrs):
            await serp_queue.put(None)

        # Wait for the serp workers to be concluded before adding the sentinels to the url_queue
        serp_workers = self._workers["serp"]
        try:
            logger.debug("Waiting for serp_workers to conclude their tasks...")
            serp_res = await asyncio.gather(*serp_workers, return_exceptions=True)
            for i, res in enumerate(serp_res):
                if isinstance(res, Exception):
                    logger.error(f"Error in serp_worker {i}: {res}")
            logger.debug("...serp_workers concluded their tasks")
        except Exception as e:
            logger.error(f"Gathering serp_workers failed: {e}")
        finally:
            await serp_queue.join()

        # ---------------------------
        #  ORCHESTRATE URL COLLECTOR
        # ---------------------------
        # Add the sentinels to the url_queue
        url_queue = self._queues["url"]
        await url_queue.put(None)

        # Wait for the url_collector to be concluded before adding the sentinels to the zyte_queue
        url_collector = cast(asyncio.Task, self._workers["url"])
        try:
            logger.debug("Waiting for url_collector to conclude its tasks...")
            await url_collector
            logger.debug("...url_collector concluded its tasks")
        except Exception as e:
            logger.error(f"Gathering url_collector failed: {e}")
        finally:
            await url_queue.join()

        # ---------------------------
        #  ORCHESTRATE ZYTE WORKERS
        # ---------------------------
        # Add the sentinels to the zyte_queue
        zyte_queue = self._queues["zyte"]
        for _ in range(n_zyte_wkrs):
            await zyte_queue.put(None)

        # Wait for the zyte_workers to be concluded before adding the sentinels to the proc_queue
        zyte_workers = self._workers["zyte"]
        try:
            logger.debug("Waiting for zyte_workers to conclude their tasks...")
            zyte_res = await asyncio.gather(*zyte_workers, return_exceptions=True)
            for i, res in enumerate(zyte_res):
                if isinstance(res, Exception):
                    logger.error(f"Error in zyte_worker {i}: {res}")
            logger.debug("...zyte_workers concluded their tasks")
        except Exception as e:
            logger.error(f"Gathering zyte_workers failed: {e}")
        finally:
            await zyte_queue.join()

        # ---------------------------
        #  ORCHESTRATE PROC WORKERS
        # ---------------------------
        # Add the sentinels to the proc_queue
        proc_queue = self._queues["proc"]
        for _ in range(n_proc_wkrs):
            await proc_queue.put(None)

        # Wait for the proc_workers to be concluded before adding the sentinels to the res_queue
        proc_workers = self._workers["proc"]
        try:
            logger.debug("Waiting for proc_workers to conclude their tasks...")
            proc_res = await asyncio.gather(*proc_workers, return_exceptions=True)
            for i, res in enumerate(proc_res):
                if isinstance(res, Exception):
                    logger.error(f"Error in proc_worker {i}: {res}")
            logger.debug("...proc_workers concluded their tasks")
        except Exception as e:
            logger.error(f"Gathering proc_workers failed: {e}")
        finally:
            await proc_queue.join()

        # ---------------------------
        #  ORCHESTRATE RES COLLECTOR
        # ---------------------------
        # Add the sentinels to the res_queue
        res_queue = self._queues["res"]
        await res_queue.put(None)

        # Wait for the res_collector to be concluded
        res_collector = cast(asyncio.Task, self._workers["res"])
        try:
            logger.debug("Waiting for res_collector to conclude its tasks...")
            await res_collector
            logger.debug("...res_collector concluded its tasks")
        except Exception as e:
            logger.error(f"Gathering res_collector failed: {e}")
        finally:
            await res_queue.join()

        # ---------------------------
        #  CLOSING PIPELINE
        # ---------------------------
        logger.info("Pipeline concluded; async framework is closed")
