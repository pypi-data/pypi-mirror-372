"""
Module for interacting with the Trade Placement Service.

This module defines a `TradePlacement` class responsible for managing and executing
equity trades such as CNC (Cash and Carry) and MTF (Margin Trading Facility) across
multiple brokers. It handles order placement, authentication, metadata construction,
and communication with external broker APIs. It supports placing buy/sell orders,
fetching order details, and executing bulk instructions.

Classes:
    TradePlacement: Extends `ApiClient` to interact with Trade Placement Service.

Dependencies:
    - bw_essentials.constants.services.Services
    - bw_essentials.services.api_client.ApiClient
    - bw_essentials.services.broker.Broker
"""
import json
import logging
from datetime import datetime

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient
from bw_essentials.services.broker import Broker

logger = logging.getLogger()


class TradePlacement(ApiClient):
    """
    Client to interact with the Trade Placement Service.

    Attributes:
        base_url (str): Base URL of the Trade Placement Service.
        broker_service_base_url (str): Base URL of the Broker Service.
        user_info (dict): User context including broker, user_id, and entity_id.
        name (str): Name of the service.
    """
    SELL = 'sell'
    BUY = 'buy'
    MARKET = 'market'
    LIMIT = 'limit'
    MTF = 'mtf'
    CNC = 'cnc'
    LKP = "lkp"
    AXIS = "axis"
    ZERODHA = "zerodha"
    PAPER_TRADE = "paper_trade"
    PL = "pl"
    EMKAY = 'emkay'
    DEALER = "dealer"
    USER = "user"

    EXECUTABLE = 'executable'
    READY_ONLY = 'read_only'
    BROKER_CONFIG_MAPPER = {
        DEALER: READY_ONLY,
        USER: EXECUTABLE
    }

    def __init__(self,
                 service_user: str,
                 user_info: dict):
        """
        Initialize TradePlacement client.

        Args:
            service_user (str): Username for service access.
            user_info (dict): Metadata including broker and user identity.
        """
        logger.info(f"Initializing TradePlacement client for user: {service_user}")
        super().__init__(user=service_user)
        self.base_url = self.get_base_url(Services.TRADE_PLACEMENT.value)
        self.user_info = user_info
        self.broker = self.user_info.get('current_broker')
        self.user_id = self.user_info.get('user_id')
        self.entity_id = self.user_info.get("entity_id")
        self.name = Services.TRADE_PLACEMENT.value
        self.urls = {
            "order": "orders/order",
            "update_orders": "orders/order/update"
        }
        if self.user_info.get("broker_name") in [self.PAPER_TRADE]:
            self._authenticate()

    def _authenticate(self):
        """
          Authenticates with the broker service if using paper trade broker.
        """
        broker = Broker(service_user=self.user)
        broker.authenticate(broker_name=self.broker,
                            user_id=self.user_id,
                            entity_id=self.user_id)

    def _get_cnc_metadata(self, user_portfolio_id, instruction_id, rebalance, user_portfolio_rebalance_id):
        """
        Build metadata dictionary for CNC (Cash and Carry) order.

        Args:
            user_portfolio_id (str): Portfolio ID of the user.
            instruction_id (str): Unique ID for the instruction.
            rebalance (bool): Indicates whether rebalance is happening.
            user_portfolio_rebalance_id (str): Unique ID for rebalance.

        Returns:
            dict: Metadata for CNC order.
        """
        user_info = self.user_info or {}

        return {
            "user_portfolio_id": user_portfolio_id,
            "instruction_id": instruction_id,
            "user_id": user_info.get("user_id"),
            "date": str(datetime.now().date()),
            "rebalance": rebalance,
            "user_portfolio_rebalance_id": user_portfolio_rebalance_id,
            "user_info": {
                "current_broker": user_info.get("current_broker"),
                "broker_name": user_info.get("broker_name"),
                "entity_id": user_info.get("entity_id")
            }
        }

    def _get_mtf_metadata(self, basket_id, instruction_id):
        """
        Build metadata dictionary for MTF (Margin Trading Facility) order.

        Args:
            basket_id (int): Basket identifier.
            instruction_id (int): Instruction identifier.

        Returns:
            dict: Metadata for MTF order.
        """
        user_info = self.user_info or {}  # Use an empty dictionary as a fallback

        return {
            "user_id": user_info.get("user_id"),
            "date": str(datetime.now().date()),
            "basket_id": basket_id,
            "instruction_id": instruction_id,
            "user_info": {
                "current_broker": user_info.get("current_broker"),
                "broker_name": user_info.get("broker_name"),
                "entity_id": user_info.get("entity_id")
            }
        }

    def _place_order(self, trading_symbol, qty, side, order_tag, meta_data, product, order_type, proxy=None,
                     asm_consent=None, asm_reason=None):
        """
        Places an order with the provided metadata and order details.

        Args:
            trading_symbol (str): Symbol to trade.
            qty (int): Quantity to trade.
            side (str): Order side ('buy' or 'sell').
            order_tag (str): Identifier tag for the order.
            meta_data (dict): Metadata about the order context.
            product (str): Type of product ('cnc' or 'mtf').
            order_type (str): Type of order ('market', 'limit').
            proxy (str, optional): Indicates if proxy config is used.
            asm_consent (str, optional): Consent for ASM if applicable.
            asm_reason (str, optional): Reason for ASM if applicable.

        Returns:
            dict: Response containing placed order details.
        """
        logger.info(f"In - _place_order {trading_symbol =}, {qty =}, {side =}, {order_tag =}"
                    f"{proxy =}")
        broker_config = self.EXECUTABLE
        if proxy == self.READY_ONLY:
            broker_config = self.READY_ONLY

        payload = json.dumps({
            "user_id": self.user_info.get("user_id"),
            "entity_id": self.user_info.get("entity_id"),
            "symbol": trading_symbol,
            "quantity": abs(qty),
            "broker": self.user_info.get("broker_name"),
            "broker_config": broker_config,
            "price": 0,
            "product_type": product,
            "order_type": order_type,
            "side": side,
            "tag": order_tag,
            "metadata": meta_data,
            "asm_consent": asm_consent,
            "asm_reason": asm_reason
        })
        placed_orders_data = self._post(url=self.base_url,
                                        endpoint=self.urls.get("order"),
                                        data=payload)
        return placed_orders_data.get("data")

    def _market_buy_cnc(self, trading_symbol, qty, generate_order_tag,
                        user_portfolio_id, instruction_id, rebalance,
                        user_portfolio_rebalance_id, proxy=None,
                        asm_consent=None, asm_reason=None):
        """
        Places a market buy order using CNC.

        Args:
            trading_symbol (str): Symbol to buy.
            qty (int): Quantity to buy.
            generate_order_tag (str): Order tag.
            user_portfolio_id (str): Portfolio ID.
            instruction_id (str): Instruction ID.
            rebalance (bool): Rebalance flag.
            user_portfolio_rebalance_id (str): Rebalance ID.
            proxy (str, optional): Proxy config.
            asm_consent (str, optional): ASM consent.
            asm_reason (str, optional): ASM reason.

        Returns:
            dict: Order response data.
        """
        logger.info(f"Placing CNC market buy order for {trading_symbol=}, {qty=}")
        meta_data = self._get_cnc_metadata(user_portfolio_id, instruction_id, rebalance, user_portfolio_rebalance_id)
        return self._place_order(trading_symbol, qty, self.BUY, generate_order_tag,
                                 meta_data, self.CNC, self.MARKET,
                                 proxy=proxy, asm_consent=asm_consent, asm_reason=asm_reason)

    def _market_sell_cnc(self, trading_symbol, qty, generate_order_tag,
                         user_portfolio_id, instruction_id, rebalance,
                         user_portfolio_rebalance_id, proxy=None,
                         asm_consent=None, asm_reason=None):
        """
        Places a market sell order using CNC.

        Args:
            trading_symbol (str): Symbol to sell.
            qty (int): Quantity to sell.
            generate_order_tag (str): Order tag.
            user_portfolio_id (str): Portfolio ID.
            instruction_id (str): Instruction ID.
            rebalance (bool): Rebalance flag.
            user_portfolio_rebalance_id (str): Rebalance ID.
            proxy (str, optional): Proxy config.
            asm_consent (str, optional): ASM consent.
            asm_reason (str, optional): ASM reason.

        Returns:
            dict: Order response data.
        """
        logger.info(f"Placing CNC market sell order for {trading_symbol=}, {qty=}")
        meta_data = self._get_cnc_metadata(user_portfolio_id, instruction_id, rebalance, user_portfolio_rebalance_id)
        return self._place_order(trading_symbol, qty, self.SELL, generate_order_tag,
                                 meta_data, self.CNC, self.MARKET,
                                 proxy=proxy, asm_consent=asm_consent, asm_reason=asm_reason)

    def _market_buy_mtf(self, trading_symbol, qty, generate_order_tag, basket_id, instruction_id, proxy=None):
        """
        Places a market buy order using MTF.

        Args:
            trading_symbol (str): Symbol to buy.
            qty (int): Quantity to buy.
            generate_order_tag (str): Order tag.
            basket_id (int): Basket ID.
            instruction_id (int): Instruction ID.
            proxy (str, optional): Proxy config.

        Returns:
            dict: Order response data.
        """
        logger.info(f"Placing MTF market buy order for {trading_symbol=}, {qty=}")
        meta_data = self._get_mtf_metadata(basket_id, instruction_id)
        return self._place_order(trading_symbol, qty, self.BUY, generate_order_tag,
                                 meta_data, self.MTF, self.MARKET, proxy=proxy)

    def _market_sell_mtf(self, trading_symbol, qty, generate_order_tag, basket_id, instruction_id, proxy=None):
        """
        Places a market sell order using MTF.

        Args:
            trading_symbol (str): Symbol to sell.
            qty (int): Quantity to sell.
            generate_order_tag (str): Order tag.
            basket_id (int): Basket ID.
            instruction_id (int): Instruction ID.
            proxy (str, optional): Proxy config.

        Returns:
            dict: Order response data.
        """
        logger.info(f"Placing MTF market sell order for {trading_symbol=}, {qty=}")
        meta_data = self._get_mtf_metadata(basket_id, instruction_id)
        return self._place_order(trading_symbol, qty, self.SELL, generate_order_tag,
                                 meta_data, self.MTF, self.MARKET, proxy=proxy)

    def get_order_details(self, order_id):
        """
        Fetch order details by order ID.

        Args:
            order_id (str): Unique ID of the order.

        Returns:
            dict: Detailed order information.
        """
        logger.info(f"Fetching order details for {order_id=}")
        order_details = self._get(url=self.base_url,
                                  endpoint=f"{self.urls.get('order')}/{order_id}")
        return order_details.get("data")

    def execute_sell_orders_cnc(self, instructions, request_data, portfolio_rebalance_id):
        """
        Executes a list of CNC sell instructions.

        Args:
            instructions (list): List of sell order dictionaries.
            request_data (dict): Metadata including portfolio info.
            portfolio_rebalance_id (str): Rebalance ID.
        """
        logger.info(f"Executing CNC sell orders - {instructions=}")
        for orders in instructions:
            data = self._market_sell_cnc(trading_symbol=orders.get("symbol"),
                                         qty=orders.get("qty"),
                                         generate_order_tag=orders.get("tag"),
                                         user_portfolio_id=request_data.get("user_portfolio_id"),
                                         instruction_id=orders.get("instruction_id"),
                                         rebalance=request_data.get("rebalance"),
                                         user_portfolio_rebalance_id=portfolio_rebalance_id,
                                         asm_consent=orders.get('asm_consent'),
                                         asm_reason=orders.get('asm_reason'))
            logger.info(f"CNC sell executed: {data=}")

    def execute_sell_orders_mtf(self, instructions, basket_id):
        """
        Executes sell orders for the Multi-Trade Fund (MTF).

        This method iterates through a list of sell instructions and places market sell
        orders for each security based on the given instructions. It uses the `_market_sell_mtf`
        method to handle the order execution.

        Args:
            instructions (list): A list of dictionaries containing sell order details.
                Each dictionary includes:
                    - "symbol" (str): The trading symbol of the security.
                    - "qty" (int): The quantity of the security to sell.
                    - "tag" (bool): Indicates whether to generate an order tag for the sell order.

            basket_id (int): The unique identifier for the basket.

        Returns:
            None
        """
        logger.info(f"In execute_orders - {instructions =}")
        for orders in instructions:
            data = self._market_sell_mtf(
                trading_symbol=orders.get("symbol"),
                qty=orders.get("qty"),
                generate_order_tag=orders.get("tag"),
                basket_id=basket_id,
                instruction_id=orders.get("instruction_id")
            )
            logger.info(f"execute_orders sell {data = }")

    def execute_buy_orders_cnc(self, instructions, request_data, portfolio_rebalance_id):
        """
        Execute a list of orders.

        Args:
        instructions (dict): Instructions for executing orders.
        """
        logger.info(f"In execute_buy_orders - {instructions =}, {request_data =}, {portfolio_rebalance_id =}")
        for orders in instructions:
            data = self._market_buy_cnc(trading_symbol=orders.get("symbol"),
                                        qty=orders.get("qty"),
                                        generate_order_tag=orders.get("tag"),
                                        user_portfolio_id=request_data.get("user_portfolio_id"),
                                        instruction_id=orders.get("instruction_id"),
                                        rebalance=request_data.get("rebalance"),
                                        user_portfolio_rebalance_id=portfolio_rebalance_id,
                                        asm_consent=orders.get('asm_consent'),
                                        asm_reason=orders.get('asm_reason')
                                        )
            logger.info(f"execute_buy_orders  {data = }")

    def execute_buy_orders_mtf(self, instructions, basket_id):
        """
        Executes buy orders for the Multi-Trade Fund (MTF).

        This method processes a list of buy instructions and places market buy
        orders for each security. It utilizes the `_market_buy_mtf` method for
        executing the orders based on the provided instructions.

        Args:
            instructions (list): A list of dictionaries containing buy order details.
                Each dictionary includes:
                    - "symbol" (str): The trading symbol of the security to buy.
                    - "qty" (int): The quantity of the security to buy.
                    - "tag" (bool): Indicates whether to generate an order tag for the buy order.
                for order processing.
            basket_id (int): The unique identifier for the basket.

        Returns:
            None
        """
        logger.info(f"In execute_buy_orders_mtf - {instructions =}")
        for orders in instructions:
            data = self._market_buy_mtf(
                trading_symbol=orders.get("symbol"),
                qty=orders.get("qty"),
                generate_order_tag=orders.get("tag"),
                basket_id=basket_id,
                instruction_id=orders.get("instruction_id")
            )
            logger.info(f"execute_buy_orders_mtf  {data = }")

    def create_draft_orders(self, instructions, request_data, portfolio_rebalance_id):
        """
        Create draft buy/sell CNC (Cash & Carry) market orders based on provided instructions.

        This method iterates over a list of order instructions and dispatches them to the appropriate
        order creation method (`_market_buy_cnc` or `_market_sell_cnc`) depending on the order side.

        Parameters:
        ----------
        instructions : list[dict]
            A list of order instruction dictionaries. Each dictionary must include:
                - 'side' : str ('BUY' or 'SELL')
                - 'symbol' : str
                - 'qty' : int
                - 'tag' : str
                - 'instruction_id' : str

        request_data : dict
            A dictionary containing contextual information about the rebalance operation.
            Must include:
                - 'user_portfolio_id' : str
                - 'rebalance' : bool or dict

        portfolio_rebalance_id : str or int
            The ID associated with the current user portfolio rebalance session.

        Raises:
        ------
        ValueError:
            If an instruction has an unrecognized `side` value.
        """
        logger.info(
            f"In draft_orders - {instructions =}, {request_data =}, {portfolio_rebalance_id =} ")

        for order in instructions:
            side = order.get("side")
            if side == self.BUY:
                method = self._market_buy_cnc
            elif side == self.SELL:
                method = self._market_sell_cnc
            else:
                raise ValueError(f"Invalid order side '{side}' for instruction: {order}")

            method(
                trading_symbol=order.get("symbol"),
                qty=order.get("qty"),
                generate_order_tag=order.get("tag"),
                user_portfolio_id=request_data.get("user_portfolio_id"),
                instruction_id=order.get("instruction_id"),
                rebalance=request_data.get("rebalance"),
                user_portfolio_rebalance_id=portfolio_rebalance_id,
                proxy=self.READY_ONLY
            )

    def update_orders(self, instructions):
        """
        Update multiple orders based on the provided instructions.

        This method takes a list of order instructions, iterates through each instruction,
        and sends a PUT request to update the order details on the broker's server.

        Args:
            instructions (list): A list of dictionaries, where each dictionary contains the details
                                 of an order that needs to be updated. Each dictionary typically
                                 includes keys such as 'tag', 'symbol', 'quantity', 'side',
                                 'order_price', etc.

        Returns:
            None

        Raises:
            HTTPError: If the PUT request to update an order fails or returns an error.

        Logs:
            - Logs the start of the update process and each order update attempt.
            - Logs detailed information about the instructions being processed.
        """
        logger.info(f"In update_orders {instructions =}")
        response = {}
        for instruction in instructions:
            tag = instruction.get('tag')
            logger.info(f"Updating order for {tag =}")
            response = self._put(
                url=self.base_url,
                endpoint=f'{self.urls.get("update_orders")}/{tag}',
                data=json.dumps(instruction)
            )
        return response
