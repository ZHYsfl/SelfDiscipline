<template>
  <div style="max-width:420px;margin:48px auto;padding:24px;border:1px solid #eee;border-radius:12px;">
    <h2 style="margin-top:0;">HeartSync 登录 / 注册</h2>
    <form @submit.prevent="onSubmit">
      <label>Email</label>
      <input v-model="email" type="email" required style="width:100%;padding:8px;margin:6px 0 12px;" />
      <label>密码</label>
      <input v-model="password" type="password" required style="width:100%;padding:8px;margin:6px 0 12px;" />
      <label>昵称（注册时可填）</label>
      <input v-model="displayName" type="text" placeholder="可选" style="width:100%;padding:8px;margin:6px 0 12px;" />
      <div style="display:flex;gap:8px;">
        <button :disabled="loading" type="submit">登录</button>
        <button :disabled="loading" @click.prevent="onRegister">注册</button>
      </div>
      <p v-if="error" style="color:#c00;margin-top:12px;">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/http'
import { setAccessToken, setRefreshToken } from '../services/auth'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const email = ref('')
const password = ref('')
const displayName = ref('')
const loading = ref(false)
const error = ref('')

async function onSubmit() {
  try {
    loading.value = true
    error.value = ''
    const { data } = await api.post('/auth/login', { email: email.value, password: password.value })
    setAccessToken(data.access_token)
    setRefreshToken(data.refresh_token)
    router.replace(route.query.redirect || '/')
  } catch (e) {
    error.value = '登录失败，请检查邮箱与密码'
  } finally {
    loading.value = false
  }
}

async function onRegister() {
  try {
    loading.value = true
    error.value = ''
    await api.post('/auth/register', { email: email.value, password: password.value, display_name: displayName.value || null })
    await onSubmit()
  } catch (e) {
    error.value = '注册失败，邮箱可能已被使用'
  } finally {
    loading.value = false
  }
}
</script>
