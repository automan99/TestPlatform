import request from './index'

/**
 * 菜单管理 API
 */
export const menuApi = {
  /**
   * 获取所有菜单列表
   */
  getList(params) {
    return request.get('/menus', { params })
  },

  /**
   * 获取菜单详情
   */
  getDetail(id) {
    return request.get(`/menus/${id}`)
  },

  /**
   * 创建菜单
   */
  create(data) {
    return request.post('/menus', data)
  },

  /**
   * 更新菜单
   */
  update(id, data) {
    return request.put(`/menus/${id}`, data)
  },

  /**
   * 删除菜单
   */
  delete(id) {
    return request.delete(`/menus/${id}`)
  },

  /**
   * 获取菜单树
   */
  getTree() {
    return request.get('/menus')
  },

  /**
   * 获取当前用户菜单
   */
  getUserMenus() {
    return request.get('/menus/user/menus')
  },

  /**
   * 批量更新菜单排序
   */
  updateSort(data) {
    return request.put('/menus/sort', data)
  }
}

/**
 * 角色管理 API
 */
export const roleApi = {
  /**
   * 获取角色列表
   */
  getList(params) {
    return request.get('/menus/roles', { params })
  },

  /**
   * 获取角色详情
   */
  getDetail(id) {
    return request.get(`/menus/roles/${id}`)
  },

  /**
   * 创建角色
   */
  create(data) {
    return request.post('/menus/roles', data)
  },

  /**
   * 更新角色
   */
  update(id, data) {
    return request.put(`/menus/roles/${id}`, data)
  },

  /**
   * 删除角色
   */
  delete(id) {
    return request.delete(`/menus/roles/${id}`)
  },

  /**
   * 获取角色的菜单权限
   */
  getMenus(roleId) {
    return request.get(`/menus/roles/${roleId}/menus`)
  },

  /**
   * 分配菜单权限给角色
   */
  assignMenus(roleId, menuIds) {
    return request.put(`/menus/roles/${roleId}/menus`, { menu_ids: menuIds })
  }
}

export default { menuApi, roleApi }
