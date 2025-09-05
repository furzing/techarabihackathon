import requests
import json
from datetime import datetime, timedelta
import time

# API base URL
BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name, success, response_data=None, error=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error": str(error) if error else None
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if error:
            print(f"   Error: {error}")
        print("-" * 50)

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            success = response.status_code == 200
            self.log_test("Health Check", success, response.json() if success else None, 
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Health Check", False, error=e)
            return False

    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            success = response.status_code == 200
            self.log_test("Root Endpoint", success, response.json() if success else None,
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Root Endpoint", False, error=e)
            return False

    def test_generate_strategy(self):
        """Test strategy generation endpoint"""
        try:
            payload = {
                "business_info": {
                    "business_name": "مقهى الأصالة",
                    "business_type": "مقهى",
                    "target_audience": "الشباب والمهنيين",
                    "location": "عمان، الأردن",
                    "unique_selling_points": "قهوة عربية أصيلة وجو تراثي"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/strategy",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("success", False) and data.get("data") is not None
            
            self.log_test("Generate Strategy", success, 
                         response.json() if response.status_code == 200 else None,
                         None if success else f"Status: {response.status_code}")
            
            # Store strategy for next test
            if success:
                self.strategy_data = response.json()["data"]
            
            return success
        except Exception as e:
            self.log_test("Generate Strategy", False, error=e)
            return False

    def test_create_marketing_plan(self):
        """Test marketing plan creation endpoint"""
        try:
            # Use strategy from previous test or default
            strategy = getattr(self, 'strategy_data', "استراتيجية تسويقية شاملة للمقهى")
            
            payload = {
                "strategy": strategy,
                "duration": "2 weeks"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/marketing-plan",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("success", False) and data.get("data") is not None
            
            self.log_test("Create Marketing Plan", success,
                         response.json() if response.status_code == 200 else None,
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Create Marketing Plan", False, error=e)
            return False

    def test_content_suggestions(self):
        """Test content suggestions endpoint"""
        try:
            payload = {
                "topic": "فوائد القهوة العربية",
                "content_type": "all",
                "target_platform": "Instagram"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/content-suggestions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("success", False) and data.get("data") is not None
            
            self.log_test("Content Suggestions", success,
                         response.json() if response.status_code == 200 else None,
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Content Suggestions", False, error=e)
            return False

    def test_create_post(self):
        """Test post creation endpoint"""
        try:
            payload = {
                "idea": "منشور عن فوائد القهوة في الصباح",
                "platform": "Instagram",
                "tone": "friendly"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/create-post",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("success", False) and data.get("data") is not None
                # Store post content for next test
                if success:
                    self.post_content = data.get("data", "محتوى المنشور")
            
            self.log_test("Create Post", success,
                         response.json() if response.status_code == 200 else None,
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Create Post", False, error=e)
            return False

    def test_schedule_post(self):
        """Test post scheduling endpoint"""
        try:
            # Use post content from previous test or default
            post_content = getattr(self, 'post_content', "محتوى تجريبي للمنشور")
            
            # Schedule for tomorrow
            tomorrow = (datetime.now() + timedelta(days=1)).date()
            
            payload = {
                "post_content": post_content,
                "scheduled_date": tomorrow.isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/api/schedule-post",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("success", False) and data.get("data") is not None
            
            self.log_test("Schedule Post", success,
                         response.json() if response.status_code == 200 else None,
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Schedule Post", False, error=e)
            return False

    def test_moderate_post(self):
        """Test post moderation endpoint"""
        try:
            # Use post content from previous test or default
            post_content = getattr(self, 'post_content', "محتوى تجريبي للمنشور يحتاج للمراجعة")
            
            payload = {
                "post_content": post_content
            }
            
            response = self.session.post(
                f"{self.base_url}/api/moderate-post",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("success", False) and data.get("data") is not None
            
            self.log_test("Moderate Post", success,
                         response.json() if response.status_code == 200 else None,
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Moderate Post", False, error=e)
            return False

    def test_invalid_endpoint(self):
        """Test invalid endpoint to check error handling"""
        try:
            response = self.session.get(f"{self.base_url}/api/invalid")
            success = response.status_code == 404
            self.log_test("Invalid Endpoint (Should Return 404)", success,
                         None, None if success else f"Expected 404, got {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Invalid Endpoint", False, error=e)
            return False

    def test_invalid_data(self):
        """Test endpoint with invalid data"""
        try:
            # Send invalid data to strategy endpoint
            payload = {
                "invalid_field": "invalid_value"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/strategy",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 for validation error
            success = response.status_code == 422
            self.log_test("Invalid Data (Should Return 422)", success,
                         None, None if success else f"Expected 422, got {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Invalid Data", False, error=e)
            return False

    def run_all_tests(self):
        """Run all tests sequentially"""
        print("🚀 Starting API Tests...")
        print("=" * 50)
        
        # List of all tests
        tests = [
            self.test_health_check,
            self.test_root_endpoint,
            self.test_generate_strategy,
            self.test_create_marketing_plan,
            self.test_content_suggestions,
            self.test_create_post,
            self.test_schedule_post,
            self.test_moderate_post,
            self.test_invalid_endpoint,
            self.test_invalid_data
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                # Small delay between tests
                time.sleep(1)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️ Some tests failed. Check the details above.")
        
        return passed == total

    def save_results(self, filename="test_results.json"):
        """Save test results to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            print(f"💾 Test results saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

def main():
    """Main function to run the tests"""
    print("🔧 Social Media Manager API Tester")
    print("Make sure your API server is running on http://localhost:8000")
    input("Press Enter to start testing...")
    
    tester = APITester()
    
    try:
        # Run all tests
        success = tester.run_all_tests()
        
        # Save results
        tester.save_results()
        
        # Exit with appropriate code
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
