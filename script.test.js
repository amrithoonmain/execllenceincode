const { add, subtract } = require('./script.js');

describe('Math Functions', () => {
  test('add function', () => {
    expect(add(1, 2)).toBe(3);
    expect(add(-1, 1)).toBe(0);
  });

  test('subtract function', () => {
    expect(subtract(3, 1)).toBe(2);
    expect(subtract(1, 1)).toBe(0);
  });
});
