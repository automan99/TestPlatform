import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tenantApi } from '@/api/tenant'

export const useTenantStore = defineStore('tenant', () => {
  const currentTenant = ref(null)
  const tenantList = ref([])

  async function loadMyTenants() {
    try {
      const res = await tenantApi.getMyTenants()
      tenantList.value = res.data?.tenants || []
      return res.data
    } catch (error) {
      console.error('Failed to load tenants:', error)
      return null
    }
  }

  async function setCurrentTenant(tenantId) {
    try {
      const res = await tenantApi.switch(tenantId)
      currentTenant.value = res.data
      localStorage.setItem('currentTenantId', tenantId)
      return res.data
    } catch (error) {
      console.error('Failed to switch tenant:', error)
      throw error
    }
  }

  function getCurrentTenant() {
    if (!currentTenant.value) {
      const tenantId = localStorage.getItem('currentTenantId')
      if (tenantId) {
        const tenant = tenantList.value.find(t => t.id === parseInt(tenantId))
        if (tenant) {
          currentTenant.value = tenant
        }
      }
    }
    return currentTenant.value
  }

  function clearCurrentTenant() {
    currentTenant.value = null
    localStorage.removeItem('currentTenantId')
  }

  return {
    currentTenant,
    tenantList,
    loadMyTenants,
    setCurrentTenant,
    getCurrentTenant,
    clearCurrentTenant
  }
})
