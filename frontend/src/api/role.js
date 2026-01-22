import request from './index'

/**
 * 角色管理 API
 */
export const roleApi = {
  /**
   * 获取角色列表
   */
  getList(params) {
    return request.get('/roles', { params })
  },

  /**
   * 获取角色详情
   */
  getDetail(id) {
    return request.get(`/roles/${id}`)
  },

  /**
   * 创建角色
   */
  create(data) {
    return request.post('/roles', data)
  },

  /**
   * 更新角色
   */
  update(id, data) {
    return request.put(`/roles/${id}`, data)
  },

  /**
   * 删除角色
   */
  delete(id) {
    return request.delete(`/roles/${id}`)
  },

  /**
   * 获取角色的菜单权限
   */
  getMenus(roleId) {
    return request.get(`/roles/${roleId}/menus`)
  },

  /**
   * 分配菜单权限给角色
   */
  assignMenus(roleId, menuIds) {
    return request.put(`/roles/${roleId}/menus`, { menu_ids: menuIds })
  },

  /**
   * 获取角色的用户列表
   */
  getUsers(roleId) {
    return request.get(`/roles/${roleId}/users`)
  },

  /**
   * 分配用户给角色
   */
  assignUsers(roleId, userIds) {
    return request.put(`/roles/${roleId}/users`, { user_ids: userIds })
  }
}

export default { roleApi }
