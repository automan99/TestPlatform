# -*- coding: utf-8 -*-

with open('AIExecution.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修复损坏的panel-header
content = content.replace(
    '''        <div class="panel-header">
          <span class="panel-title">用例执行</span>
          <!-- 移除旧的执行按钮 -->
            执行
          </el-button>
        </div>''',
    '''        <div class="panel-header">
          <span class="panel-title">用例执行</span>
          <div class="header-actions">
            <el-tooltip content="执行" placement="top">
              <el-button type="primary" :icon="VideoPlay" size="small" circle @click="handleExecuteAll" />
            </el-tooltip>
            <el-tooltip content="重新执行" placement="top">
              <el-button :icon="Refresh" size="small" circle @click="handleReExecute" />
            </el-tooltip>
            <el-tooltip content="修改用例" placement="top">
              <el-button :icon="Edit" size="small" circle @click="handleModifyCase" />
            </el-tooltip>
            <el-tooltip content="清除缓存" placement="top">
              <el-button :icon="Delete" size="small" circle @click="handleClearCache" />
            </el-tooltip>
          </div>
        </div>'''
)

# 2. 移除底部的action-buttons部分
content = content.replace(
    '''        <!-- 底部操作按钮 -->
        <div class="action-buttons">
          <el-button :icon="Refresh" @click="handleReExecute">重新执行</el-button>
          <el-button :icon="Edit" @click="handleModifyCase">修改用例</el-button>
          <el-button :icon="Delete" @click="handleClearCache">清除缓存</el-button>
        </div>
      </div>''',
    '''      </div>'''
)

# 3. 移除action-buttons的CSS样式
import re
content = re.sub(
    r'\.action-buttons \{[^}]+\}(?:\n\s*\}[^}]*\}|\s*\}[^}]*\})*',
    '',
    content,
    flags=re.DOTALL
)

# 4. 添加header-actions样式
content = content.replace(
    '''.panel-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}''',
    '''.panel-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
}'''
)

with open('AIExecution.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("AI执行页面修复完成")
