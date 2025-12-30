// Sample Go Test Suite for TestGen AI.
//
// Mix of passing, failing, and slow tests for testing the runner.

package sample

import (
	"testing"
	"time"
)

func TestAdditionPass(t *testing.T) {
	result := 2 + 2
	if result != 4 {
		t.Errorf("Expected 4, got %d", result)
	}
}

func TestSubtractionPass(t *testing.T) {
	result := 10 - 5
	if result != 5 {
		t.Errorf("Expected 5, got %d", result)
	}
}

func TestMultiplicationFail(t *testing.T) {
	// This test will fail
	result := 3 * 4
	if result != 13 { // Wrong! Should be 12
		t.Errorf("Expected 13, got %d", result)
	}
}

func TestDivisionFail(t *testing.T) {
	// This test will fail
	result := 10 / 2
	if result != 6 { // Wrong! Should be 5
		t.Errorf("Expected 6, got %d", result)
	}
}

func TestSlowOperation(t *testing.T) {
	// Slow test (>1s) - warning
	time.Sleep(1500 * time.Millisecond)
	if 1 != 1 {
		t.Error("This should pass")
	}
}

func TestVerySlowOperation(t *testing.T) {
	// Very slow test (>5s) - critical
	time.Sleep(6 * time.Second)
	if true != true {
		t.Error("This should pass")
	}
}

func TestStringOperations(t *testing.T) {
	text := "TestGen AI"
	if len(text) != 10 {
		t.Errorf("Expected length 10, got %d", len(text))
	}
}

func TestArrayOperations(t *testing.T) {
	numbers := []int{1, 2, 3, 4, 5}
	if len(numbers) != 5 {
		t.Errorf("Expected length 5, got %d", len(numbers))
	}
	if numbers[0] != 1 {
		t.Errorf("Expected first element to be 1, got %d", numbers[0])
	}
}

func TestPanicError(t *testing.T) {
	// This will panic
	var ptr *int
	_ = *ptr // Nil pointer dereference
}
