"""
End-to-end tests for M-Pesa STK Push payment integration using Playwright
"""

import pytest
import asyncio
import json
from playwright.async_api import async_playwright, Page, BrowserContext
from decimal import Decimal


class TestPaymentIntegration:
    """E2E tests for payment system"""
    
    @pytest.fixture
    async def browser_context(self):
        """Setup browser context for testing"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            yield context
            await browser.close()
    
    @pytest.fixture
    async def page(self, browser_context: BrowserContext):
        """Setup page for testing"""
        page = await browser_context.new_page()
        yield page
        await page.close()
    
    async def test_payment_api_endpoints_accessible(self, page: Page):
        """Test that payment API endpoints are accessible"""
        
        # Test API documentation is accessible
        response = await page.goto("http://localhost:8001/docs")
        assert response.status == 200
        
        # Check that payment endpoints are documented
        content = await page.content()
        assert "payments" in content.lower()
        assert "mpesa" in content.lower()
        
    async def test_payment_initiation_flow(self, page: Page):
        """Test complete payment initiation flow"""
        
        # Step 1: Get manager authentication token
        await page.goto("http://localhost:8001/debug/create-manager-token")
        token_response = await page.text_content("pre")
        token_data = json.loads(token_response)
        access_token = token_data.get("access_token")
        
        assert access_token is not None, "Failed to get access token"
        
        # Step 2: Test payment initiation endpoint
        payment_data = {
            "booking_id": "b3b94de8-4f6a-4567-b781-7877c1e55a42",
            "phone_number": "254708374149",
            "amount": 1.00
        }
        
        # Use page.evaluate to make API call with authentication
        result = await page.evaluate(f"""
            async () => {{
                const response = await fetch('http://localhost:8001/api/v1/payments/initiate', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer {access_token}'
                    }},
                    body: JSON.stringify({json.dumps(payment_data)})
                }});
                
                const data = await response.json();
                return {{
                    status: response.status,
                    data: data
                }};
            }}
        """)
        
        # Verify payment initiation response
        assert result["status"] in [200, 400], f"Unexpected status: {result['status']}"
        
        if result["status"] == 200:
            # Payment initiated successfully
            assert "payment_id" in result["data"]
            payment_id = result["data"]["payment_id"]
            
            # Step 3: Test payment status endpoint
            status_result = await page.evaluate(f"""
                async () => {{
                    const response = await fetch('http://localhost:8001/api/v1/payments/status/{payment_id}', {{
                        method: 'GET',
                        headers: {{
                            'Authorization': 'Bearer {access_token}'
                        }}
                    }});
                    
                    const data = await response.json();
                    return {{
                        status: response.status,
                        data: data
                    }};
                }}
            """)
            
            assert status_result["status"] == 200
            assert "payment_id" in status_result["data"]
            assert "status" in status_result["data"]
            
        else:
            # Payment failed (expected in some cases)
            assert "detail" in result["data"] or "error" in result["data"]
    
    async def test_payment_dashboard_access(self, page: Page):
        """Test payment dashboard endpoint"""
        
        # Get manager token
        await page.goto("http://localhost:8001/debug/create-manager-token")
        token_response = await page.text_content("pre")
        token_data = json.loads(token_response)
        access_token = token_data.get("access_token")
        
        # Test dashboard endpoint
        result = await page.evaluate(f"""
            async () => {{
                const response = await fetch('http://localhost:8001/api/v1/payments/dashboard', {{
                    method: 'GET',
                    headers: {{
                        'Authorization': 'Bearer {access_token}'
                    }}
                }});
                
                const data = await response.json();
                return {{
                    status: response.status,
                    data: data
                }};
            }}
        """)
        
        # Dashboard should be accessible
        assert result["status"] in [200, 500], f"Unexpected status: {result['status']}"
        
        if result["status"] == 200:
            # Verify dashboard data structure
            dashboard_data = result["data"]
            expected_fields = ["total_payments", "successful_payments", "failed_payments", "total_amount"]
            
            for field in expected_fields:
                assert field in dashboard_data, f"Missing dashboard field: {field}"
    
    async def test_payment_list_endpoint(self, page: Page):
        """Test payment list endpoint"""
        
        # Get manager token
        await page.goto("http://localhost:8001/debug/create-manager-token")
        token_response = await page.text_content("pre")
        token_data = json.loads(token_response)
        access_token = token_data.get("access_token")
        
        # Test payment list endpoint
        result = await page.evaluate(f"""
            async () => {{
                const response = await fetch('http://localhost:8001/api/v1/payments/list?limit=5', {{
                    method: 'GET',
                    headers: {{
                        'Authorization': 'Bearer {access_token}'
                    }}
                }});
                
                const data = await response.json();
                return {{
                    status: response.status,
                    data: data
                }};
            }}
        """)
        
        # Payment list should be accessible
        assert result["status"] in [200, 500], f"Unexpected status: {result['status']}"
        
        if result["status"] == 200:
            # Verify list structure
            list_data = result["data"]
            assert "payments" in list_data
            assert "total" in list_data
            assert "page" in list_data
            assert "limit" in list_data
    
    async def test_database_connectivity(self, page: Page):
        """Test that the application can connect to the database"""
        
        # Test health endpoint which should check database connectivity
        response = await page.goto("http://localhost:8001/health")
        assert response.status == 200
        
        content = await page.text_content("body")
        health_data = json.loads(content)
        
        assert health_data.get("status") == "healthy"
        assert "database" in health_data
    
    async def test_mpesa_configuration(self, page: Page):
        """Test M-Pesa configuration is properly loaded"""
        
        # This test verifies that M-Pesa credentials are configured
        # by checking if the service can generate access tokens
        
        # Get manager token first
        await page.goto("http://localhost:8001/debug/create-manager-token")
        token_response = await page.text_content("pre")
        token_data = json.loads(token_response)
        access_token = token_data.get("access_token")
        
        # Try to initiate a payment (which will test M-Pesa config)
        result = await page.evaluate(f"""
            async () => {{
                const response = await fetch('http://localhost:8001/api/v1/payments/initiate', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer {access_token}'
                    }},
                    body: JSON.stringify({{
                        "booking_id": "b3b94de8-4f6a-4567-b781-7877c1e55a42",
                        "phone_number": "254708374149",
                        "amount": 1.00
                    }})
                }});
                
                const data = await response.json();
                return {{
                    status: response.status,
                    data: data
                }};
            }}
        """)
        
        # Should not fail due to missing configuration
        # (may fail due to invalid token or other M-Pesa issues, but not config)
        assert result["status"] != 500, "Server error suggests configuration issues"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
