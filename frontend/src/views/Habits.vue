<template>
  <div style="max-width:800px;margin:24px auto;padding:16px;">
    <h2>习惯管理</h2>
    <form @submit.prevent="create" style="display:flex;gap:8px;align-items:center;margin-bottom:12px;flex-wrap:wrap;">
      <input v-model="name" placeholder="名称，例如 起床、睡觉、绩点" />
      <select v-model="type">
        <option value="boolean">勾选</option>
        <option value="number">数字</option>
        <option value="text">文字</option>
        <option value="time">时间(HH:MM)</option>
      </select>
      <button type="submit">添加</button>
    </form>
    <div v-for="h in habits" :key="h.id" style="display:flex;gap:8px;align-items:center;border-bottom:1px solid #eee;padding:8px 0;">
      <span style="width:240px;">{{ h.name }} ({{ h.type }})</span>
      <label><input type="checkbox" v-model="h.is_active" @change="update(h)" />启用</label>
      <input type="number" v-model.number="h.order_index" @change="update(h)" style="width:80px;" />
      <button @click="remove(h)">删除</button>
    </div>
  </div>
  
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/http'

const habits = ref([])
const name = ref('')
const type = ref('boolean')

async function fetchHabits() {
  const { data } = await api.get('/habits/')
  habits.value = data
}

async function create() {
  if (!name.value) return
  const { data } = await api.post('/habits/', { name: name.value, type: type.value, is_active: true, order_index: habits.value.length })
  habits.value.push(data)
  name.value = ''
}

async function update(h) {
  const { data } = await api.patch(`/habits/${h.id}`, { is_active: h.is_active, order_index: h.order_index })
  Object.assign(h, data)
}

async function remove(h) {
  await api.delete(`/habits/${h.id}`)
  habits.value = habits.value.filter(x => x.id !== h.id)
}

onMounted(fetchHabits)
</script>
