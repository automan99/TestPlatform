import { defineStore } from 'pinia'
import { ref } from 'vue'
import { testSuiteApi, testCaseApi } from '@/api/test-case'

export const useTestCaseStore = defineStore('testCase', () => {
  // 状态
  const suites = ref([])
  const cases = ref([])
  const currentSuite = ref(null)
  const currentCase = ref(null)
  const selectedCases = ref([])
  const loading = ref(false)

  // Actions
  async function fetchSuites(params) {
    loading.value = true
    try {
      const res = await testSuiteApi.getTree(params)
      suites.value = res.data || []
      return res
    } finally {
      loading.value = false
    }
  }

  async function fetchCases(params) {
    loading.value = true
    try {
      const res = await testCaseApi.getList(params)
      cases.value = res.data?.items || []
      return res
    } finally {
      loading.value = false
    }
  }

  async function createSuite(data) {
    return await testSuiteApi.create(data)
  }

  async function updateSuite(id, data) {
    return await testSuiteApi.update(id, data)
  }

  async function deleteSuite(id) {
    return await testSuiteApi.delete(id)
  }

  async function createCase(data) {
    return await testCaseApi.create(data)
  }

  async function updateCase(id, data) {
    return await testCaseApi.update(id, data)
  }

  async function deleteCase(id) {
    return await testCaseApi.delete(id)
  }

  async function batchDeleteCases(caseIds) {
    return await testCaseApi.batchDelete({ case_ids: caseIds })
  }

  async function batchMoveCases(caseIds, targetSuiteId) {
    return await testCaseApi.batchMove({
      case_ids: caseIds,
      target_suite_id: targetSuiteId
    })
  }

  function setCurrentSuite(suite) {
    currentSuite.value = suite
  }

  function setCurrentCase(c) {
    currentCase.value = c
  }

  function toggleCaseSelection(caseId) {
    const index = selectedCases.value.indexOf(caseId)
    if (index > -1) {
      selectedCases.value.splice(index, 1)
    } else {
      selectedCases.value.push(caseId)
    }
  }

  function clearSelection() {
    selectedCases.value = []
  }

  return {
    suites,
    cases,
    currentSuite,
    currentCase,
    selectedCases,
    loading,
    fetchSuites,
    fetchCases,
    createSuite,
    updateSuite,
    deleteSuite,
    createCase,
    updateCase,
    deleteCase,
    batchDeleteCases,
    batchMoveCases,
    setCurrentSuite,
    setCurrentCase,
    toggleCaseSelection,
    clearSelection
  }
})
