<template>
  <div class="card-page-bg" :class="{ 'bg-hide': phase === 'shrink' || phase === 'reveal' }" :style="{ backgroundImage: `url(${bgImg})` }">
    <div class="card-overlay" :class="{ 'bg-hide': phase === 'shrink' || phase === 'reveal' }">
  <div class="page-container card-page">

    <!-- Stack → Fan → Pick → Shrink phase -->
    <template v-if="phase !== 'reveal'">
      <div class="stage">
        <!-- Slot outlines -->
        <div v-for="n in MAX_CARDS" :key="'s'+n"
          class="slot-outline"
          :class="{ filled: n <= picked.length, show: phase === 'pick' }"
          :style="getSlotOutlineStyle(n - 1)">
          <span v-if="n > picked.length" class="slot-q">?</span>
        </div>

        <!-- Fan cards -->
        <div v-for="i in CARD_COUNT" :key="i"
          class="card-anim"
          :class="{
            pickable: phase === 'pick' && !picked.includes(i - 1) && picked.length < MAX_CARDS,
            'unpicked-hide': phase === 'shrink' && !picked.includes(i - 1),
          }"
          :style="getCardStyle(i - 1)"
          @click="pickCard(i - 1)">
          <div class="card-back">
            <span class="card-symbol">&#10022;</span>
          </div>
        </div>
      </div>

      <p class="pick-hint" :class="{ 'hint-hide': phase === 'shrink' }">{{ picked.length === 0 ? '请选择牌' : `已选 ${picked.length} 张` }}</p>

      <div class="confirm-area" :class="{ 'hint-hide': phase === 'shrink' }">
        <button class="btn-primary" :disabled="picked.length === 0 || confirming" @click="confirm">
          {{ confirming ? '占卜中...' : '确认选牌' }}
        </button>
      </div>
    </template>

    <!-- Reveal phase -->
    <div class="reveal-container" v-if="phase === 'reveal'">
      <div class="reveal-cards">
        <div v-for="(card, i) in readingStore.cardsDrawn" :key="i"
          class="reveal-card"
          :class="{ flipped: revealedIndices.includes(i) }">
          <div class="reveal-card-inner">
            <div class="reveal-card-front">
              <span class="card-symbol">&#10022;</span>
            </div>
            <div class="reveal-card-back">
              <span class="reveal-name">{{ card.name_cn }}</span>
              <span class="reveal-pos">{{ { past: '过去', present: '现在', future: '未来' }[card.position] }}</span>
              <span class="reveal-dir" v-if="card.is_reversed">逆位</span>
            </div>
          </div>
        </div>
      </div>

      <div class="reading-box fade-in" v-if="showReading">
        <div class="reading-label">&#10022; 占卜师的低语 &#10022;</div>
        <p class="reading-text">{{ displayedText }}<span class="cursor" v-if="isTyping">|</span></p>
      </div>

      <div class="cta fade-in" v-if="!isTyping && showReading">
        <button class="btn-primary" @click="router.push(`/payment/${readingStore.currentReadingId}`)">
          解锁完整解读
        </button>
        <button class="btn-back" @click="router.push(props.skipToReveal ? '/profile' : '/fortune')">返回</button>
      </div>
    </div>
  </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useReadingStore } from '../stores/reading'
import { getReading, selectCards, generateShareImage } from '../api/reading'
import bgImg from '../assets/taroter.jpg'

const props = defineProps({ skipToReveal: Boolean })
const router = useRouter()
const route = useRoute()
const readingStore = useReadingStore()

const CARD_COUNT = 78
const FAN_SPREAD = 150
const FAN_RADIUS = 200
const CW = 46, CH = 72
const SLOT_SPACING = 66
const SLOT_Y = 92
const MAX_CARDS = 3

// Reveal target positions — must match .reveal-container CSS exactly
// reveal-container padding-top:10px + reveal-cards margin:16px = 26px from top
// flex gap:14px, card width:80px → center-to-center = 80+14 = 94px
const REVEAL_SPACING = 94
const REVEAL_Y_PX = 26
const RW = 80, RH = 120

const phase = ref('stack') // stack → fan → pick → shrink → reveal
const picked = ref([])
const confirming = ref(false)
const revealedIndices = ref([])
const showReading = ref(false)
const displayedText = ref('')
const isTyping = ref(false)

function getFanPos(index) {
  const angle = -FAN_SPREAD / 2 + (FAN_SPREAD / (CARD_COUNT - 1)) * index
  const rad = angle * Math.PI / 180
  const x = Math.sin(rad) * FAN_RADIUS
  const y = FAN_RADIUS - Math.cos(rad) * FAN_RADIUS
  return { x, y, angle }
}

function slotX(slotIndex) {
  return (slotIndex - 1) * SLOT_SPACING
}

function revealX(slotIndex) {
  return (slotIndex - 1) * REVEAL_SPACING
}

function getSlotOutlineStyle(slotIndex) {
  const pad = 6
  return {
    left: `calc(50% + ${slotX(slotIndex)}px - ${CW / 2 + pad}px)`,
    top: `calc(${SLOT_Y}% - ${CH / 2 + pad}px)`,
  }
}

function getCardStyle(i) {
  // Stacked
  if (phase.value === 'stack') {
    return {
      left: `calc(50% - ${CW / 2}px)`,
      top: `calc(50vh - ${CH}px)`,
      width: CW + 'px',
      height: CH + 'px',
      transform: `rotate(${(i - CARD_COUNT / 2) * 0.2}deg)`,
      zIndex: i,
      pointerEvents: 'none',
    }
  }

  // Picked cards
  const slotIdx = picked.value.indexOf(i)
  if (slotIdx !== -1) {
    // Shrink phase → move to reveal position and grow
    if (phase.value === 'shrink') {
      return {
        left: `calc(50% + ${revealX(slotIdx)}px - ${RW / 2}px)`,
        top: `${REVEAL_Y_PX}px`,
        width: RW + 'px',
        height: RH + 'px',
        transform: 'rotate(0deg)',
        zIndex: 30 + slotIdx,
        pointerEvents: 'none',
      }
    }
    // Pick phase → in slot
    return {
      left: `calc(50% + ${slotX(slotIdx)}px - ${CW / 2}px)`,
      top: `calc(${SLOT_Y}% - ${CH / 2}px)`,
      width: CW + 'px',
      height: CH + 'px',
      transform: 'rotate(0deg)',
      zIndex: 30 + slotIdx,
      pointerEvents: 'none',
    }
  }

  // Fan / unpicked
  const pos = getFanPos(i)
  const full = phase.value === 'pick' && picked.value.length >= 3
  return {
    left: `calc(50% + ${pos.x}px - ${CW / 2}px)`,
    top: `calc(50vh - ${CH}px + ${pos.y}px)`,
    width: CW + 'px',
    height: CH + 'px',
    transform: `rotate(${pos.angle}deg)`,
    zIndex: i,
    opacity: full || phase.value === 'shrink' ? 0 : 1,
    pointerEvents: phase.value === 'pick' && !full ? 'auto' : 'none',
  }
}

function pickCard(i) {
  if (phase.value !== 'pick') return
  if (picked.value.includes(i)) {
    // Deselect: remove from picked
    picked.value = picked.value.filter(p => p !== i)
    // Sync count to backend
    selectCards(readingStore.currentReadingId, picked.value.length)
    return
  }
  if (picked.value.length >= MAX_CARDS) return
  picked.value.push(i)
  // Sync count to backend
  selectCards(readingStore.currentReadingId, picked.value.length)
}

async function confirm() {
  if (picked.value.length === 0) return
  confirming.value = true
  try {
    if (readingStore.readingPromise) await readingStore.readingPromise
    if (readingStore.readingError || !readingStore.currentReadingId) {
      alert('占卜失败，请重试')
      router.push('/fortune')
      return
    }

    // Confirm selection: backend will set status=brief and return full cards+brief
    const { data } = await confirmSelection(readingStore.currentReadingId)
    readingStore.briefReading = data.brief_reading || ''
    readingStore.cardsDrawn = data.cards_drawn || []

    // Phase 1: shrink
    phase.value = 'shrink'
    await new Promise(r => setTimeout(r, 1200))

    // Phase 2: reveal
    phase.value = 'reveal'
    await startReveal()
  } finally {
    confirming.value = false
  }
}

async function startReveal() {
  const count = readingStore.cardsDrawn?.length || picked.value.length
  for (let i = 0; i < count; i++) {
    await new Promise(r => setTimeout(r, 800))
    revealedIndices.value.push(i)
  }
  await new Promise(r => setTimeout(r, 600))
  showReading.value = true
  startTypewriter()
}

function startTypewriter() {
  const fullText = readingStore.briefReading || ''
  displayedText.value = ''
  isTyping.value = true
  let idx = 0
  const interval = setInterval(() => {
    if (idx < fullText.length) {
      displayedText.value += fullText[idx]
      idx++
    } else {
      clearInterval(interval)
      isTyping.value = false
    }
  }, 30)
}

onMounted(async () => {
  // Skip directly to reveal for history re-entry — fetch from API
  if (props.skipToReveal) {
    const readingId = route.params.readingId
    if (!readingId) {
      router.push('/profile')
      return
    }
    try {
      const { data } = await getReading(readingId)
      readingStore.currentReadingId = data.id
      readingStore.cardsDrawn = data.cards_drawn || []
      readingStore.briefReading = data.brief_reading || ''
      readingStore.status = data.status

      if (data.status === 'draft') {
        // Resume card selection
        phase.value = 'fan'
        setTimeout(() => { phase.value = 'pick' }, 900)
        return
      }
    } catch {
      router.push('/profile')
      return
    }
    phase.value = 'reveal'
    await startReveal()
    return
  }
  setTimeout(() => { phase.value = 'fan' }, 200)
  setTimeout(() => { phase.value = 'pick' }, 1100)
})
</script>

<style scoped>
.card-page-bg {
  min-height: 100vh;
  background-size: auto 75vh;
  background-position: center top;
  background-repeat: no-repeat;
  background-color: #0a051e;
  transition: opacity 1s ease;
}
.card-page-bg.bg-hide {
  background-image: none !important;
}
.card-overlay {
  min-height: 100vh;
  background: linear-gradient(to bottom, rgba(10,5,30,0) 0%, rgba(10,5,30,0) 40%, rgba(10,5,30,0.7) 60%, rgba(10,5,30,0.95) 80%, rgba(10,5,30,1) 100%);
  transition: background 1s ease;
}
.card-overlay.bg-hide {
  background: rgba(10, 5, 30, 1);
}
.card-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.stage {
  position: relative;
  flex: 1;
  min-height: 50vh;
}

/* Slot outlines */
.slot-outline {
  position: absolute;
  width: 58px;
  height: 84px;
  border: 2px dashed rgba(246, 211, 101, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  opacity: 0;
  transition: opacity 0.8s ease, border-color 0.3s;
}
.slot-outline.show {
  opacity: 1;
}
.slot-outline.filled {
  border-color: var(--color-accent);
  background: rgba(246, 211, 101, 0.06);
}
.slot-q {
  font-size: 22px;
  color: rgba(246, 211, 101, 0.35);
}

/* Fan cards */
.card-anim {
  position: absolute;
  transition: all 1.2s cubic-bezier(0.23, 1, 0.32, 1);
}
.card-anim.pickable {
  cursor: pointer;
}
.card-anim.pickable:hover {
  filter: brightness(1.3);
}
.card-anim.unpicked-hide {
  opacity: 0 !important;
  pointer-events: none !important;
}

.card-back {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #3d2080, #5b2d99);
  border: 2px solid var(--color-accent);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card-symbol {
  font-size: 18px;
  color: var(--color-accent);
}

.pick-hint {
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin-bottom: 8px;
  transition: opacity 0.6s ease;
}
.confirm-area {
  padding: 0 16px 20px;
  transition: opacity 0.6s ease;
}
.hint-hide {
  opacity: 0;
  pointer-events: none;
}

/* ---- Reveal phase ---- */
.reveal-container { padding-top: 10px; }
.reveal-cards { display: flex; justify-content: center; gap: 14px; margin: 16px 0; }
.reveal-card { width: 80px; height: 120px; perspective: 600px; }
.reveal-card-inner {
  width: 100%; height: 100%; position: relative;
  transform-style: preserve-3d; transition: transform 0.6s ease;
}
.reveal-card.flipped .reveal-card-inner { transform: rotateY(180deg); }
.reveal-card-front, .reveal-card-back {
  position: absolute; width: 100%; height: 100%;
  backface-visibility: hidden; border-radius: 8px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.reveal-card-front {
  background: linear-gradient(135deg, #3d2080, #5b2d99);
  border: 2px solid var(--color-accent);
}
.reveal-card-back {
  background: linear-gradient(135deg, #1a0a3e, #2d1b69);
  border: 2px solid var(--color-primary-light);
  transform: rotateY(180deg); gap: 4px;
}
.reveal-name { font-size: 14px; color: var(--color-accent); font-weight: bold; }
.reveal-pos { font-size: 11px; color: var(--color-text-muted); }
.reveal-dir { font-size: 10px; color: var(--color-accent-pink); }
.reading-box {
  background: rgba(255,255,255,0.05); border-radius: var(--radius);
  padding: 16px 18px; margin: 16px 0;
}
.reading-label {
  font-size: var(--font-size-sm); color: var(--color-primary-light);
  margin-bottom: 10px; letter-spacing: 2px; text-align: center;
}
.reading-text { font-size: var(--font-size-base); line-height: 1.8; color: var(--color-text); white-space: pre-wrap; }
.cursor { animation: blink 0.8s infinite; color: var(--color-accent); }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
.cta { margin-top: 8px; padding-bottom: 20px; display: flex; flex-direction: column; gap: 10px; }
.btn-back {
  background: none; border: 1px solid var(--color-border);
  padding: 12px; border-radius: var(--radius); color: var(--color-text-muted);
  font-size: var(--font-size-base);
}
</style>
