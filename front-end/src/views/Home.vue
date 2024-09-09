<template>
 <h5>HALLO ALBANO</h5>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { reactive, ref } from 'vue'
import Home from './Home.vue'

const data = reactive({
  selectedComp: sessionStorage.getItem('comp') ?? 'Welcome',
})

const router = useRouter()

const components = reactive([
  Home
])

const navItems = ref([
  { title: 'Home',
    icon: 'fa fa-home',
    component: 'Home',
    route: '/',
    disabled: false,
    link: true
  },
])

function updateRoute(route, comp) {
  sessionStorage.setItem('comp', comp.toString())
  data.selectedComp = comp
  router.push({ path: route })
}

</script>

<style lang="scss" scoped>
</style>


