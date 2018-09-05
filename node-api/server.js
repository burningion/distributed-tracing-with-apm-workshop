const tracer = require('dd-trace').init({hostname:'agent'})
const express = require('express')
const app = express()

app.get('/', (req, res) => {
    res.send({'hello': 'world'})
})

app.listen(5003, () => console.log('Example app listening on port 5003!'))
