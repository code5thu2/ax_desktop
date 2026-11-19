<script setup lang="ts">
import McpStudioView from './McpStudioView.vue'

interface Props {
  appendTo?: string | HTMLElement
  showList?: boolean
  embedded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  appendTo: 'body',
  showList: true,
  embedded: false,
})
</script>

<template>
  <McpStudioView
    :append-to="props.appendTo"
    :show-list="props.showList"
    :embedded="props.embedded"
  />
</template>
