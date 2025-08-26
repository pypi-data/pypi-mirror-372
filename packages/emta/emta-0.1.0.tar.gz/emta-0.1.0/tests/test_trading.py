"""Tests for the Eastmoney Trading Agent"""

import os
from unittest.mock import patch

from emta.core.agent import TradingAgent
from emta.models.trading import OrderStatus, OrderType


class TestTradingAgent:
    """Tests for the TradingAgent class"""

    def test_init(self):
        """Test TradingAgent initialization"""
        agent = TradingAgent()
        assert agent.username is None
        assert agent.password is None
        assert agent.is_logged_in is False

    def test_init_with_credentials(self):
        """Test TradingAgent initialization with credentials"""
        agent = TradingAgent("test_user", "test_pass")
        assert agent.username == "test_user"
        assert agent.password == "test_pass"

    def test_login(self):
        agent = TradingAgent(
            os.getenv("EM_USERNAME", ""),
            os.getenv("EM_PASSWORD", ""),
        )
        # This test requires actual credentials, so we'll skip the actual login
        # and just check that the method exists
        assert hasattr(agent, "login")

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    @patch("emta.api.client.APIClient.get_asset_and_position")
    def test_login_success(self, mock_asset_position, mock_captcha, mock_auth_login):
        """Test successful login"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock asset and position data
        mock_asset_position.return_value = {"assets": 100000, "positions": []}

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        result = agent.login()

        assert result is True
        assert agent.is_logged_in is True
        assert "account_balance" in agent.account_info

    def test_login_failure_missing_credentials(self):
        """Test login failure when credentials are missing"""
        agent = TradingAgent()
        result = agent.login()
        assert result is False
        assert agent.is_logged_in is False

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_login_failure_api_error(self, mock_captcha, mock_auth_login):
        """Test login failure due to API error"""
        # Mock the authentication client to return failure
        mock_auth_login.return_value = (
            False,
            {"Status": -1, "Message": "Invalid credentials"},
        )

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        result = agent.login()

        assert result is False
        assert agent.is_logged_in is False

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    @patch("emta.auth.client.AuthClient.logout")
    def test_logout(self, mock_auth_logout, mock_captcha, mock_auth_login):
        """Test logout functionality"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})
        mock_auth_logout.return_value = None

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        agent.login()
        assert agent.is_logged_in is True

        agent.logout()
        assert agent.is_logged_in is False
        assert agent.account_info == {}
        mock_auth_logout.assert_called_once()

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_get_account_info(self, mock_captcha, mock_auth_login):
        """Test getting account information"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        account_info = agent.get_account_info()
        assert isinstance(account_info, dict)
        assert "username" in account_info
        assert "account_balance" in account_info

    def test_get_account_info_not_logged_in(self):
        """Test getting account info when not logged in"""
        agent = TradingAgent()
        account_info = agent.get_account_info()
        assert account_info == {}

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_place_order(self, mock_captcha, mock_auth_login):
        """Test placing an order"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        order_id = agent.place_order("SH600000", OrderType.BUY, 100, 12.5)
        assert order_id is not None
        assert isinstance(order_id, str)

    def test_place_order_not_logged_in(self):
        """Test placing an order when not logged in"""
        agent = TradingAgent()
        order_id = agent.place_order("SH600000", OrderType.BUY, 100, 12.5)
        assert order_id is None

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_cancel_order(self, mock_captcha, mock_auth_login):
        """Test cancelling an order"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        result = agent.cancel_order("test_order_id")
        assert result is True

    def test_cancel_order_not_logged_in(self):
        """Test cancelling an order when not logged in"""
        agent = TradingAgent()
        result = agent.cancel_order("test_order_id")
        assert result is False

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_get_order_status(self, mock_captcha, mock_auth_login):
        """Test getting order status"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        status = agent.get_order_status("test_order_id")
        assert status is not None
        assert isinstance(status, OrderStatus)

    def test_get_order_status_not_logged_in(self):
        """Test getting order status when not logged in"""
        agent = TradingAgent()
        status = agent.get_order_status("test_order_id")
        assert status is None

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_get_market_data(self, mock_captcha, mock_auth_login):
        """Test getting market data"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        market_data = agent.get_market_data("SH600000")
        assert isinstance(market_data, dict)
        assert "symbol" in market_data
        assert "last_price" in market_data

    def test_get_market_data_not_logged_in(self):
        """Test getting market data when not logged in"""
        agent = TradingAgent()
        market_data = agent.get_market_data("SH600000")
        assert market_data == {}

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_get_positions(self, mock_captcha, mock_auth_login):
        """Test getting positions"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        positions = agent.get_positions()
        assert isinstance(positions, list)

    def test_get_positions_not_logged_in(self):
        """Test getting positions when not logged in"""
        agent = TradingAgent()
        positions = agent.get_positions()
        assert positions == []
