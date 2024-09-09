import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import * as labs from 'vuetify/labs/components'

export default createVuetify({
    components: {
        ...components,
        ...labs
    },
    directives,
    theme: {
        defaultTheme: 'dark'
    },
})
