<template>
  <div style="max-width:900px;margin:16px auto;padding:12px;">
    <header style="display:flex;justify-content:space-between;align-items:center;">
      <h2>今天</h2>
      <nav style="display:flex;gap:8px;align-items:center;">
        <router-link to="/pair">配对</router-link>
        <router-link to="/habits">习惯</router-link>
        <a :href="apiBase + '/docs'" target="_blank">API</a>
      </nav>
    </header>
    <p v-if="!tasks.length" style="color:#666;">先到 配对/习惯 配置后开始打卡</p>

    <div v-for="t in tasks" :key="t.habit.id" style="border:1px solid #eee;border-radius:10px;padding:12px;margin:12px 0;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <b>{{ t.habit.name }}</b>
        <small>{{ t.habit.type }}</small>
      </div>
      <div style="display:flex;gap:12px;align-items:center;margin:8px 0;">
        <span>我：</span>
        <component :is="inputFor(t.habit.type)" v-model="meInputs[t.habit.id]" />
        <input type="file" @change="onFile($event, t.habit.id)" />
        <input placeholder="备注" v-model="notes[t.habit.id]" />
        <button @click="submit(t.habit.id)">提交</button>
      </div>
      <div v-if="t.me?.image_url"><img :src="apiBase + t.me.image_url" style="max-height:100px;" /></div>
      <div style="color:#555;">对方：<span>{{ displayCheckin(t.partner, t.habit.type) }}</span></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, defineComponent } from 'vue'
import api from '../services/http'

const apiBase = import.meta.env.VITE_API_BASE
const tasks = ref([])
const meInputs = reactive({})
const notes = reactive({})
const files = reactive({})

const BooleanInput = defineComponent({
  props: ['modelValue'],
  emits: ['update:modelValue'],
  template: `<label><input type="checkbox" :checked="modelValue" @change="$emit('update:modelValue', $event.target.checked)" /> 完成</label>`
})
const NumberInput = defineComponent({
  props: ['modelValue'],
  emits: ['update:modelValue'],
  template: `<input type="number" :value="modelValue" @input="$emit('update:modelValue', Number($event.target.value))" placeholder="数字" />`
})
const TextInput = defineComponent({
  props: ['modelValue'],
  emits: ['update:modelValue'],
  template: `<input :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" placeholder="文字" />`
})
const TimeInput = defineComponent({
  props: ['modelValue'],
  emits: ['update:modelValue'],
  template: `<input type="time" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" />`
})

function inputFor(type) {
  return type === 'boolean' ? BooleanInput : type === 'number' ? NumberInput : type === 'time' ? TimeInput : TextInput
}

function displayCheckin(ci, type) {
  if (!ci) return '未打卡'
  const map = { boolean: ci.value_bool ? '完成' : '未完成', number: ci.value_number, text: ci.value_text, time: ci.value_time }
  return map[type] ?? ''
}

function onFile(e, habitId) {
  files[habitId] = e.target.files?.[0]
}

async function fetchToday() {
  const { data } = await api.get('/overview/today')
  tasks.value = data.tasks
}

async function submit(habitId) {
  const form = new FormData()
  const task = tasks.value.find(t => t.habit.id === habitId)
  const type = task.habit.type
  const val = meInputs[habitId]
  if (type === 'boolean') form.append('value_bool', val ? 'true' : 'false')
  if (type === 'number' && val != null) form.append('value_number', String(val))
  if (type === 'text' && val) form.append('value_text', val)
  if (type === 'time' && val) form.append('value_time', val)
  if (notes[habitId]) form.append('note', notes[habitId])
  if (files[habitId]) form.append('image', files[habitId])
  const { data } = await api.post(`/checkins/${habitId}`, form)
  await fetchToday()
}

onMounted(fetchToday)
</script>
