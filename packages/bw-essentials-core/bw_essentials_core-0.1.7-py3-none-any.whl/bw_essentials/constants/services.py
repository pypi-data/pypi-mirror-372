from enum import Enum


class Services(Enum):
    """
    Enumeration of available services.
    """
    REBALANCE_BUSINESS = 'Rebalance_Business'
    REBALANCE = 'Rebalance'
    MASTER_DATA = 'Master_Data'
    MARKET_PRICER = "Market_Pricer"
    BROKER = 'Broker'
    USER_PORTFOLIO = 'User_Portfolio'
    TRADE_PLACEMENT = 'Trade_Placement'
    CONTENT = 'Portfolio_Content'
    NOTIFICATION = 'Notification'
    USER_REPORTING = 'User_Reporting'
    PAYMENT = 'Payment'
    MODEL_PORTFOLIO = "Model_Portfolio"
    PROMETHEUS_USER_APP = "Prometheus_User_App"
    PORTFOLIO_CATALOGUE = "Portfolio_Catalogue"
    PORTFOLIO_CONTENT = "Portfolio_Content"

class PortfolioStatus(Enum):
    """
        Enum representing Status of Basket.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"

    ACTIVE_FOR_SUBSCRIBED_USER = (ACTIVE, PAUSED)
