"""Tests for the Eastmoney Trading Agent"""

import os
from unittest.mock import MagicMock, patch

from loguru import logger

from emta.core.agent import TradingAgent
from emta.models.trading import OrderStatus, OrderType


class TestTradingAgent:
    """Tests for the TradingAgent class"""

    def test_init(self) -> None:
        """Test TradingAgent initialization"""
        agent = TradingAgent()
        assert agent.username is None
        assert agent.password is None
        assert agent.is_logged_in is False

    def test_init_with_credentials(self) -> None:
        """Test TradingAgent initialization with credentials"""
        agent = TradingAgent("test_user", "test_pass")
        assert agent.username == "test_user"
        assert agent.password == "test_pass"

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    @patch("emta.api.client.APIClient.get_asset_and_position")
    def test_login(
        self,
        mock_asset_position: MagicMock,
        mock_captcha: MagicMock,
        mock_auth_login: MagicMock,
    ) -> None:
        """Test TradingAgent login with credentials from environment variables"""
        logger.info("test_login")

        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock asset and position data with proper structure
        mock_asset_position.return_value = {
            "Data": [
                {
                    "Djzj": 100000,
                    "Dryk": 5000,
                    "Kqzj": 95000,
                    "Kyzj": 80000,
                    "Ljyk": 10000,
                    "Money_type": "RMB",
                    "RMBZzc": 120000,
                    "Zjye": 100000,
                    "Zxsz": 110000,
                    "Zzc": 120000,
                    "positions": [],
                }
            ]
        }

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent(
            os.getenv("EM_USERNAME", "test_user"),
            os.getenv("EM_PASSWORD", "test_pass"),
        )
        result = agent.login()

        assert result is True
        assert agent.is_logged_in is True
        # Verify that login was called with the correct parameters
        mock_auth_login.assert_called_once_with(
            os.getenv("EM_USERNAME", "test_user"),
            os.getenv("EM_PASSWORD", "test_pass"),
            30,
            3,
            1.0,
        )

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    @patch("emta.api.client.APIClient.get_asset_and_position")
    def test_login_success(
        self,
        mock_asset_position: MagicMock,
        mock_captcha: MagicMock,
        mock_auth_login: MagicMock,
    ) -> None:
        """Test successful login"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock asset and position data with proper structure
        mock_asset_position.return_value = {
            "Data": [
                {
                    "Djzj": 100000,
                    "Dryk": 5000,
                    "Kqzj": 95000,
                    "Kyzj": 80000,
                    "Ljyk": 10000,
                    "Money_type": "RMB",
                    "RMBZzc": 120000,
                    "Zjye": 100000,
                    "Zxsz": 110000,
                    "Zzc": 120000,
                    "positions": [],
                }
            ]
        }

        # Mock the captcha
        mock_captcha.return_value = None

        agent = TradingAgent("test_user", "test_pass")
        result = agent.login()

        assert result is True
        assert agent.is_logged_in is True
        # Verify that login was called with the correct parameters
        mock_auth_login.assert_called_once_with("test_user", "test_pass", 30, 3, 1.0)

    def test_login_failure_missing_credentials(self) -> None:
        """Test login failure when credentials are missing"""
        agent = TradingAgent()
        result = agent.login()
        assert result is False
        assert agent.is_logged_in is False

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_login_failure_api_error(
        self, mock_captcha: MagicMock, mock_auth_login: MagicMock
    ) -> None:
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
        # Verify that login was called with the correct parameters
        mock_auth_login.assert_called_once_with("test_user", "test_pass", 30, 3, 1.0)

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    @patch("emta.auth.client.AuthClient.logout")
    def test_logout(
        self,
        mock_auth_logout: MagicMock,
        mock_captcha: MagicMock,
        mock_auth_login: MagicMock,
    ) -> None:
        """Test logout functionality"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})
        mock_auth_logout.return_value = None

        # Mock asset and position data with proper structure
        with patch(
            "emta.api.client.APIClient.get_asset_and_position"
        ) as mock_asset_position:
            mock_asset_position.return_value = {
                "Data": [
                    {
                        "Djzj": 100000,
                        "Dryk": 5000,
                        "Kqzj": 95000,
                        "Kyzj": 80000,
                        "Ljyk": 10000,
                        "Money_type": "RMB",
                        "RMBZzc": 120000,
                        "Zjye": 100000,
                        "Zxsz": 110000,
                        "Zzc": 120000,
                        "positions": [],
                    }
                ]
            }

            # Mock the captcha
            mock_captcha.return_value = None

            agent = TradingAgent("test_user", "test_pass")
            agent.login()
            # Set the validate_key to simulate successful login
            agent.auth_client.validate_key = "test_validate_key"
            assert agent.is_logged_in is True
            # Verify that login was called with the correct parameters
            mock_auth_login.assert_called_once_with(
                "test_user", "test_pass", 30, 3, 1.0
            )

            agent.logout()
            assert agent.is_logged_in is False
            assert agent.account_info == []
            mock_auth_logout.assert_called_once()

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_get_account_info(
        self, mock_captcha: MagicMock, mock_auth_login: MagicMock
    ) -> None:
        """Test getting account information"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        # Mock asset and position data with proper structure
        with patch(
            "emta.api.client.APIClient.get_asset_and_position"
        ) as mock_asset_position:
            mock_asset_position.return_value = {
                "Data": [
                    {
                        "Djzj": 100000,
                        "Dryk": 5000,
                        "Kqzj": 95000,
                        "Kyzj": 80000,
                        "Ljyk": 10000,
                        "Money_type": "RMB",
                        "RMBZzc": 120000,
                        "Zjye": 100000,
                        "Zxsz": 110000,
                        "Zzc": 120000,
                        "positions": [],
                    }
                ]
            }

            agent = TradingAgent("test_user", "test_pass")
            agent.login()
            # Set the validate_key to simulate successful login
            agent.auth_client.validate_key = "test_validate_key"

            account_info = agent.get_account_info()
            assert isinstance(account_info, dict)
            assert "username" in account_info
            assert "account_balance" in account_info
            # Verify that login was called with the correct parameters
            mock_auth_login.assert_called_once_with(
                "test_user", "test_pass", 30, 3, 1.0
            )

    def test_get_account_info_not_logged_in(self) -> None:
        """Test getting account info when not logged in"""
        agent = TradingAgent()
        account_info = agent.get_account_info()
        assert account_info == []

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_place_order(
        self, mock_captcha: MagicMock, mock_auth_login: MagicMock
    ) -> None:
        """Test placing an order"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        # Mock asset and position data with proper structure
        with patch(
            "emta.api.client.APIClient.get_asset_and_position"
        ) as mock_asset_position:
            mock_asset_position.return_value = {
                "Data": [
                    {
                        "Djzj": 100000,
                        "Dryk": 5000,
                        "Kqzj": 95000,
                        "Kyzj": 80000,
                        "Ljyk": 10000,
                        "Money_type": "RMB",
                        "RMBZzc": 120000,
                        "Zjye": 100000,
                        "Zxsz": 110000,
                        "Zzc": 120000,
                        "positions": [],
                    }
                ]
            }

            agent = TradingAgent("test_user", "test_pass")
            agent.login()

            # Set the validate_key to simulate successful login
            agent.auth_client.validate_key = "test_validate_key"

            order_id = agent.place_order("SH600000", OrderType.BUY, 100, 12.5)
            assert order_id is not None
            assert isinstance(order_id, str)
            # Verify that login was called with the correct parameters
            mock_auth_login.assert_called_once_with(
                "test_user", "test_pass", 30, 3, 1.0
            )

    def test_place_order_not_logged_in(self) -> None:
        """Test placing an order when not logged in"""
        agent = TradingAgent()
        order_id = agent.place_order("SH600000", OrderType.BUY, 100, 12.5)
        assert order_id is None

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_cancel_order(
        self, mock_captcha: MagicMock, mock_auth_login: MagicMock
    ) -> None:
        """Test cancelling an order"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        # Mock asset and position data with proper structure
        with patch(
            "emta.api.client.APIClient.get_asset_and_position"
        ) as mock_asset_position:
            mock_asset_position.return_value = {
                "Data": [
                    {
                        "Djzj": 100000,
                        "Dryk": 5000,
                        "Kqzj": 95000,
                        "Kyzj": 80000,
                        "Ljyk": 10000,
                        "Money_type": "RMB",
                        "RMBZzc": 120000,
                        "Zjye": 100000,
                        "Zxsz": 110000,
                        "Zzc": 120000,
                        "positions": [],
                    }
                ]
            }

            agent = TradingAgent("test_user", "test_pass")
            agent.login()
            # Set the validate_key to simulate successful login
            agent.auth_client.validate_key = "test_validate_key"

            result = agent.cancel_order("test_order_id")
            assert result is True
            # Verify that login was called with the correct parameters
            mock_auth_login.assert_called_once_with(
                "test_user", "test_pass", 30, 3, 1.0
            )

    def test_cancel_order_not_logged_in(self) -> None:
        """Test cancelling an order when not logged in"""
        agent = TradingAgent()
        result = agent.cancel_order("test_order_id")
        assert result is False

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_get_order_status(
        self, mock_captcha: MagicMock, mock_auth_login: MagicMock
    ) -> None:
        """Test getting order status"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        # Mock asset and position data with proper structure
        with patch(
            "emta.api.client.APIClient.get_asset_and_position"
        ) as mock_asset_position:
            mock_asset_position.return_value = {
                "Data": [
                    {
                        "Djzj": 100000,
                        "Dryk": 5000,
                        "Kqzj": 95000,
                        "Kyzj": 80000,
                        "Ljyk": 10000,
                        "Money_type": "RMB",
                        "RMBZzc": 120000,
                        "Zjye": 100000,
                        "Zxsz": 110000,
                        "Zzc": 120000,
                        "positions": [],
                    }
                ]
            }

            agent = TradingAgent("test_user", "test_pass")
            agent.login()
            # Set the validate_key to simulate successful login
            agent.auth_client.validate_key = "test_validate_key"

            status = agent.get_order_status("test_order_id")
            assert status is not None
            assert isinstance(status, OrderStatus)
            # Verify that login was called with the correct parameters
            mock_auth_login.assert_called_once_with(
                "test_user", "test_pass", 30, 3, 1.0
            )

    def test_get_order_status_not_logged_in(self) -> None:
        """Test getting order status when not logged in"""
        agent = TradingAgent()
        status = agent.get_order_status("test_order_id")
        assert status is None

    @patch("emta.auth.client.AuthClient.login")
    @patch("emta.auth.client.AuthClient._get_captcha")
    def test_get_market_data(
        self, mock_captcha: MagicMock, mock_auth_login: MagicMock
    ) -> None:
        """Test getting market data"""
        # Mock the authentication client
        mock_auth_login.return_value = (True, {"Status": 0, "Message": "Success"})

        # Mock the captcha
        mock_captcha.return_value = None

        # Mock asset and position data with proper structure
        with patch(
            "emta.api.client.APIClient.get_asset_and_position"
        ) as mock_asset_position:
            mock_asset_position.return_value = {
                "Data": [
                    {
                        "Djzj": 100000,
                        "Dryk": 5000,
                        "Kqzj": 95000,
                        "Kyzj": 80000,
                        "Ljyk": 10000,
                        "Money_type": "RMB",
                        "RMBZzc": 120000,
                        "Zjye": 100000,
                        "Zxsz": 110000,
                        "Zzc": 120000,
                        "positions": [],
                    }
                ]
            }

            agent = TradingAgent("test_user", "test_pass")
            agent.login()
            # Set the validate_key to simulate successful login
            agent.auth_client.validate_key = "test_validate_key"

            market_data = agent.get_market_data("SH600000")
            assert isinstance(market_data, dict)
            assert "symbol" in market_data
            assert "last_price" in market_data
            # Verify that login was called with the correct parameters
            mock_auth_login.assert_called_once_with(
                "test_user", "test_pass", 30, 3, 1.0
            )

    def test_get_market_data_not_logged_in(self) -> None:
        """Test getting market data when not logged in"""
        agent = TradingAgent()
        market_data = agent.get_market_data("SH600000")
        assert market_data == {}
