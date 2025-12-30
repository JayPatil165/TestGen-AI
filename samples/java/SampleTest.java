/**
 * Sample Java Test Suite for TestGen AI.
 * 
 * Mix of passing, failing, and slow tests for testing the runner.
 */

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Disabled;
import static org.junit.jupiter.api.Assertions.*;

public class SampleTest {
    
    @Test
    public void testAdditionPass() {
        assertEquals(4, 2 + 2);
    }
    
    @Test
    public void testSubtractionPass() {
        assertEquals(5, 10 - 5);
    }
    
    @Test
    public void testMultiplicationFail() {
        // This test will fail
        assertEquals(13, 3 * 4); // Wrong! Should be 12
    }
    
    @Test
    public void testDivisionFail() {
        // This test will fail
        assertEquals(6, 10 / 2); // Wrong! Should be 5
    }
    
    @Test
    public void testSlowOperation() throws InterruptedException {
        // Slow test (>1s) - warning
        Thread.sleep(1500);
        assertTrue(true);
    }
    
    @Test
    public void testVerySlowOperation() throws InterruptedException {
        // Very slow test (>5s) - critical
        Thread.sleep(6000);
        assertTrue(true);
    }
    
    @Test
    public void testNullPointerException() {
        // This will throw NullPointerException
        String text = null;
        assertEquals(5, text.length()); // Will fail
    }
    
    @Test
    public void testStringOperations() {
        String text = "TestGen AI";
        assertEquals(10, text.length());
        assertTrue(text.contains("Gen"));
    }
    
    @Test
    public void testArrayOperations() {
        int[] numbers = {1, 2, 3, 4, 5};
        assertEquals(5, numbers.length);
        assertEquals(1, numbers[0]);
    }
    
    @Disabled("Demonstrating skipped test")
    @Test
    public void testSkipped() {
        fail("This test should be skipped");
    }
}
