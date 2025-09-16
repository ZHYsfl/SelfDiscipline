<template>
  <div style="max-width:680px;margin:24px auto;padding:16px;">
    <h2>配对</h2>
    <div v-if="myCode" style="padding:12px;border:1px dashed #aaa;border-radius:8px;margin-bottom:16px;">
      你的配对码：<b>{{ myCode }}</b>
    </div>
    <div style="display:flex;gap:8px;">
      <button @click="createPair">创建配对码</button>
      <input v-model="joinCode" placeholder="输入对方的配对码" />
      <button @click="joinPair">加入</button>
    </div>
    <p v-if="msg" style="color:#090;">{{ msg }}</p>
  </div>
  
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/http'

const myCode = ref('')
const joinCode = ref('')
const msg = ref('')

async function fetchMine() {
  const { data } = await api.get('/pair/me')
  myCode.value = data[0]?.code || ''
}

async function createPair() {
  const { data } = await api.post('/pair/create')
  myCode.value = data.code
}

async function joinPair() {
  if (!joinCode.value) return
  await api.post('/pair/join', { code: joinCode.value.trim() })
  msg.value = '加入成功！'
  fetchMine()
}

onMounted(fetchMine)
</script>
