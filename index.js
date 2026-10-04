const path = require('path')
const cors = require('cors')
const express = require('express')

const app = express()
const PORT = process.env.PORT || 12315

app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`)
    next()
})

app.use(cors())

app.all('/', (req, res) => {
    res.send('https://github.com/anosu/dotabyss-translation')
})

Array.from(['manifest', 'names', 'titles', 'descriptions', 'novels', 'ui_texts', 'static', 'replacements']).forEach(cls => {
    const handler = (req, res) => {
        const filePath = path.join(__dirname, 'translations', `${cls}/${req.params[0]}`)
        res.sendFile(filePath, err => err && res.sendStatus(404))
    }
    // 兼容 CDN 地址带不带 /translations 前缀两种请求形式
    app.get([`/${cls}/*`, `/translations/${cls}/*`], handler)
})

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`)
})
