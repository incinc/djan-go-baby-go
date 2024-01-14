import { defineStore } from 'pinia'

export const useProjectStore = defineStore('something', {
  state: () => ({}),
  actions: {
    doSomething(obj) {
      console.log(obj)
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useProjectStore, import.meta.hot))
}
