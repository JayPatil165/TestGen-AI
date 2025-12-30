/**
 * Sample JavaScript Test Suite for TestGen AI.
 * 
 * Mix of passing, failing, and slow tests for testing the runner.
 */

// Helper function to simulate slow operations
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

describe('Calculator Tests', () => {
  test('addition should pass', () => {
    expect(2 + 2).toBe(4);
  });

  test('subtraction should pass', () => {
    expect(10 - 5).toBe(5);
  });

  test('multiplication should pass', () => {
    expect(3 * 4).toBe(12);
  });

  test('division should fail', () => {
    // This test will fail
    expect(10 / 2).toBe(6); // Wrong! Should be 5
  });
});

describe('String Tests', () => {
  test('string concatenation should pass', () => {
    const result = 'Hello' + ' ' + 'World';
    expect(result).toBe('Hello World');
  });

  test('string length should fail', () => {
    const text = 'TestGen';
    expect(text.length).toBe(10); // Wrong! Length is 7
  });
});

describe('Performance Tests', () => {
  test('slow operation (warning)', async () => {
    // This should trigger warning (>1s)
    await sleep(1500);
    expect(true).toBe(true);
  });

  test('very slow operation (critical)', async () => {
    // This should trigger critical warning (>5s)
    await sleep(6000);
    expect(true).toBe(true);
  }, 10000); // Increased timeout
});

describe('Error Tests', () => {
  test('should throw exception', () => {
    expect(() => {
      throw new Error('Test exception');
    }).toThrow('Test exception');
  });

  test('undefined property access should fail', () => {
    const obj = null;
    // This will fail
    expect(obj.property).toBe(undefined);
  });
});

describe('Array Tests', () => {
  test('array operations should pass', () => {
    const arr = [1, 2, 3, 4, 5];
    expect(arr.length).toBe(5);
    expect(arr[0]).toBe(1);
    expect(arr).toContain(3);
  });
});

describe.skip('Skipped Tests', () => {
  test('this test is skipped', () => {
    expect(false).toBe(true);
  });
});
