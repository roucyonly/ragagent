<template>
  <div class="page-container" style="justify-content: center;">
    <h1 class="page-title">解锁完整解读</h1>
    <p class="page-subtitle">获取详细的塔罗占卜报告</p>

    <div class="price-card fade-in">
      <div class="price-amount">
        <span class="price-symbol">&#165;</span>
        <span class="price-value">{{ (price / 100).toFixed(2) }}</span>
      </div>
      <div class="price-desc">完整塔罗占卜报告</div>
      <ul class="price-features">
        <li>逐牌详细解读</li>
        <li>牌间关联分析</li>
        <li>专属建议</li>
        <li>精美分享图片</li>
      </ul>
    </div>

    <div class="payment-methods fade-in">
      <div class="method" :class="{ active: method === 'wechat' }" @click="method = 'wechat'">
        <span class="method-icon">&#128176;</span>
        <span>微信支付</span>
      </div>
      <div class="method" :class="{ active: method === 'alipay' }" @click="method = 'alipay'">
        <span class="method-icon">&#128179;</span>
        <span>支付宝</span>
      </div>
    </div>

    <button class="btn-primary" @click="handlePay" :disabled="paying">
      {{ paying ? '处理中...' : '确认支付' }}
    </button>

    <button class="btn-mock" @click="handleMockPay" v-if="orderNo">
      [开发] 模拟支付成功
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createOrder, getOrderStatus, mockPay } from '../api/payment'

const router = useRouter()
const route = useRoute()
const readingId = route.params.readingId

const price = ref(990)
const method = ref('wechat')
const paying = ref(false)
const orderNo = ref('')

async function handlePay() {
  paying.value = true
  try {
    const { data } = await createOrder({ reading_id: readingId, payment_method: method.value })
    orderNo.value = data.out_trade_no
    price.value = data.amount_cents
    pollStatus(data.out_trade_no)
  } catch (e) {
    alert('创建订单失败')
  } finally {
    paying.value = false
  }
}

async function handleMockPay() {
  if (!orderNo.value) return
  try {
    await mockPay(orderNo.value)
    router.push(`/detail/${readingId}`)
  } catch (e) {
    alert('模拟支付失败')
  }
}

function pollStatus(outTradeNo) {
  const timer = setInterval(async () => {
    try {
      const { data } = await getOrderStatus(outTradeNo)
      if (data.status === 'paid') {
        clearInterval(timer)
        router.push(`/detail/${readingId}`)
      }
    } catch {}
  }, 2000)
  setTimeout(() => clearInterval(timer), 120000)
}
</script>

<style scoped>
.price-card {
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius); padding: 24px; text-align: center; margin-bottom: 20px;
}
.price-amount { margin-bottom: 8px; }
.price-symbol { font-size: var(--font-size-lg); color: var(--color-accent); }
.price-value { font-size: 40px; font-weight: bold; color: var(--color-accent); }
.price-desc { color: var(--color-text-muted); font-size: var(--font-size-sm); margin-bottom: 16px; }
.price-features { list-style: none; text-align: left; }
.price-features li { padding: 6px 0; color: var(--color-text); font-size: var(--font-size-sm); }
.price-features li::before { content: '✓ '; color: var(--color-success); }
.payment-methods { display: flex; gap: 12px; margin-bottom: 20px; }
.method {
  flex: 1; padding: 14px; background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); text-align: center; cursor: pointer; transition: all 0.3s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.method.active { border-color: var(--color-accent); background: rgba(246,211,101,0.1); }
.method-icon { font-size: 20px; }
.btn-mock {
  display: block; width: 100%; margin-top: 12px; padding: 10px;
  background: transparent; border: 1px dashed var(--color-border); border-radius: var(--radius-sm);
  color: var(--color-text-muted); font-size: var(--font-size-sm);
}
</style>
