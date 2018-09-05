const tracer = require('dd-trace').init({hostname:'agent'})
const express = require('express')
const app = express()

app.get('/', (req, res) => {
    res.send({'hello': 'world'})
})

app.get('/users', (req, res) => {
    res.send({'users': [{'name': 'user1', 'id': 1},
                        {'name': 'user2', 'id': 2},
                        {'name': 'user3', 'id': 3}]})
})

app.listen(5003, () => console.log('Example app listening on port 5003!'))
