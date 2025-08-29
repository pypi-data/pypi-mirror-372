"""
Bot Detection Results DTOs

Pydantic models for bot detection results from the frontend scanner.
Based on TypeScript interfaces from botDetection.ts
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class TestResult(BaseModel):
    """Individual test result from bot detection"""
    
    name: str = Field(..., description="Name of the test")
    status: Literal["passed", "failed", "warn"] = Field(..., description="Test status")
    value: Any = Field(..., description="Test result value (can be any type)")
    description: str = Field(..., description="Human-readable test description")
    score: int = Field(..., ge=0, le=100, description="Suspicion score (0-100, higher = more suspicious)")


class BotDetectionSummary(BaseModel):
    """Summary statistics for bot detection tests"""
    
    passed: int = Field(..., ge=0, description="Number of tests that passed")
    failed: int = Field(..., ge=0, description="Number of tests that failed")
    warnings: int = Field(..., ge=0, description="Number of tests with warnings")
    total: int = Field(..., ge=0, description="Total number of tests run")


class BotDetectionResults(BaseModel):
    """Complete bot detection results from frontend scanner"""
    
    tests: List[TestResult] = Field(..., description="List of individual test results")
    overall_score: int = Field(..., ge=0, le=100, description="Overall suspicion score (0-100)", alias="overallScore")
    is_bot: bool = Field(..., description="Whether the browser is detected as a bot", alias="isBot")
    confidence: Literal["low", "medium", "high"] = Field(..., description="Confidence level of detection")
    summary: BotDetectionSummary = Field(..., description="Summary statistics")
    
    model_config = {
        "json_encoders": {
            # Handle Any type serialization
            Any: lambda v: v
        },
        # Allow population by field name or alias
        "populate_by_name": True
    }
        
    @property
    def failed_tests(self) -> List[TestResult]:
        """Get list of failed tests"""
        return [test for test in self.tests if test.status == "failed"]
    
    @property
    def critical_failures(self) -> List[TestResult]:
        """Get list of critical failures that strongly indicate bot detection"""
        critical_test_names = [
            "BotD Detection",
            "WebDriver Property", 
            "Headless Chrome",
            "Chrome Object Consistency",
            "Navigator WebDriver",
            "Advanced Automation Detection"
        ]
        
        return [
            test for test in self.failed_tests 
            if any(critical in test.name for critical in critical_test_names)
        ]
    
    @property
    def warning_tests(self) -> List[TestResult]:
        """Get list of tests with warnings"""
        return [test for test in self.tests if test.status == "warn"]
    
    @property
    def passed_tests(self) -> List[TestResult]:
        """Get list of passed tests"""
        return [test for test in self.tests if test.status == "passed"]
    
    def get_effectiveness_rating(self) -> str:
        """Get stealth effectiveness rating based on results"""
        if self.overall_score <= 10 and not self.is_bot:
            return "excellent"
        elif self.overall_score <= 25 and not self.is_bot:
            return "good"
        elif self.overall_score <= 50:
            return "moderate"
        else:
            return "poor"
    
    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_test_names = [test.name for test in self.failed_tests]
        
        if any("BotD" in name for name in failed_test_names):
            recommendations.append("Consider using headed mode instead of headless for better BotD bypass")
            
        if any("WebDriver" in name for name in failed_test_names):
            recommendations.append("Enhance webdriver property removal techniques")
            
        if any("Chrome Object" in name for name in failed_test_names):
            recommendations.append("Improve window.chrome object spoofing")
            
        if any("Plugin" in name for name in failed_test_names):
            recommendations.append("Add more realistic browser plugin simulation")
            
        if any("WebGL" in name for name in failed_test_names):
            recommendations.append("Enhance WebGL vendor/renderer spoofing")
            
        if self.overall_score > 30:
            recommendations.append("Consider using undetected-chromedriver or NoDriver for better results")
            
        if len(self.critical_failures) > 2:
            recommendations.append("Multiple critical failures detected - review stealth configuration")
        
        return recommendations


class BotDetectionError(BaseModel):
    """Error information when bot detection fails"""
    
    error: str = Field(..., description="Error message")
    error_type: str = Field(default="detection_error", description="Type of error")
    timestamp: Optional[str] = Field(None, description="When the error occurred")
    
    
class BotDetectionResponse(BaseModel):
    """Response wrapper for bot detection results"""
    
    success: bool = Field(..., description="Whether detection was successful")
    results: Optional[BotDetectionResults] = Field(None, description="Detection results if successful")
    error: Optional[BotDetectionError] = Field(None, description="Error information if failed")
    scanner_url: Optional[str] = Field(None, description="URL of the scanner used")
    method: Optional[str] = Field(None, description="Stealth method used")
    timestamp: Optional[str] = Field(None, description="When the detection was performed")
    
    @classmethod
    def success_response(
        cls, 
        results: BotDetectionResults, 
        scanner_url: Optional[str] = None,
        method: Optional[str] = None
    ) -> "BotDetectionResponse":
        """Create a successful response"""
        return cls(
            success=True,
            results=results,
            scanner_url=scanner_url,
            method=method
        )
    
    @classmethod
    def error_response(
        cls, 
        error_message: str, 
        error_type: str = "detection_error",
        scanner_url: Optional[str] = None,
        method: Optional[str] = None
    ) -> "BotDetectionResponse":
        """Create an error response"""
        return cls(
            success=False,
            error=BotDetectionError(error=error_message, error_type=error_type),
            scanner_url=scanner_url,
            method=method
        )


# Type aliases for convenience
BotTestResult = TestResult
BotSummary = BotDetectionSummary
BotResults = BotDetectionResults
