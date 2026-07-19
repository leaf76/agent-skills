/**
 * Test Template for TypeScript (Vitest/Jest)
 * 
 * Usage:
 *   npx vitest run src/__tests__/module.test.ts
 *   npx jest src/__tests__/module.test.ts
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
// For Jest: import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';

// Import your module
// import { myFunction, MyClass } from '../module';

describe('myFunction', () => {
  it('should return expected output for normal input', () => {
    // Arrange
    const input = 'test';
    const expected = 'expected';

    // Act
    const result = myFunction(input);

    // Assert
    expect(result).toBe(expected);
  });

  it('should handle empty input', () => {
    expect(myFunction('')).toBeNull();
  });

  it('should throw on null input', () => {
    expect(() => myFunction(null)).toThrow('Input required');
  });

  it.each([
    ['a', 'A'],
    ['hello', 'HELLO'],
    ['123', '123'],
  ])('should transform "%s" to "%s"', (input, expected) => {
    expect(myFunction(input)).toBe(expected);
  });
});

describe('MyClass', () => {
  let instance: MyClass;

  beforeEach(() => {
    instance = new MyClass({ name: 'test' });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should initialize with correct values', () => {
    expect(instance.name).toBe('test');
    expect(instance.createdAt).toBeInstanceOf(Date);
  });

  it('should process data correctly', async () => {
    const result = await instance.process({ value: 42 });
    
    expect(result).toMatchObject({
      success: true,
      value: 42,
    });
  });

  describe('with mocked dependency', () => {
    beforeEach(() => {
      vi.spyOn(externalService, 'fetch').mockResolvedValue({ status: 'ok' });
    });

    it('should call external service', async () => {
      await instance.doSomething();
      
      expect(externalService.fetch).toHaveBeenCalledOnce();
      expect(externalService.fetch).toHaveBeenCalledWith(
        expect.objectContaining({ id: instance.id })
      );
    });

    it('should handle service failure', async () => {
      vi.spyOn(externalService, 'fetch').mockRejectedValue(new Error('Network error'));
      
      await expect(instance.doSomething()).rejects.toThrow('Network error');
    });
  });
});

describe('API Integration', () => {
  // Skip in CI if needed
  it.skipIf(process.env.CI)('should connect to real API', async () => {
    const response = await fetch('https://api.example.com/health');
    expect(response.ok).toBe(true);
  });
});

// Snapshot testing
describe('Component rendering', () => {
  it('should match snapshot', () => {
    const output = renderToString(<MyComponent name="test" />);
    expect(output).toMatchSnapshot();
  });
});

// Test utilities
const createTestUser = (overrides = {}) => ({
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
  ...overrides,
});

const createTestConfig = (overrides = {}) => ({
  debug: true,
  apiUrl: 'http://localhost:3000',
  ...overrides,
});

// Mock factory
const createMockRepository = () => ({
  findById: vi.fn(),
  save: vi.fn(),
  delete: vi.fn(),
});
