// Sample test file for API testing
const mrapids = require('mrapids');

describe('User API Tests', () => {
  test('List all users', async () => {
    const response = await mrapids.run('specs/api.yaml', {
      operation: 'listUsers'
    });
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);
  });

  test('Get specific user', async () => {
    const response = await mrapids.run('specs/api.yaml', {
      operation: 'getUser',
      params: { id: 1 }
    });
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('id');
  });
});
