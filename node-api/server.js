const tracer = require('dd-trace').init({hostname:'agent'})
const express = require('express')
const app = express()

users = {'users': [{'name': 'City of Dorondo', 'id': 1, 'demand_gph': 100},
        {'name': 'Cortland County', 'id': 2, 'demand_gph': 200},
        {'name': 'C3 Energy', 'id': 3, 'demand_gph': 4000}]}

app.get('/', (req, res) => {
    res.send({'Hello from Water Usage': 'World!'})
})

app.get('/users', async (req, res) => {
    await res.send(users)
})

app.get('/users-alt', (req, res) => {
    res.send(users)
})

app.post('/users/:userId(\\d+)/:waterLevel(\\d+)', async (req, res) => {
    try {
        const waterLevel = parseInt(req.params.waterLevel)
        const userId = parseInt(req.params.userId)
        await res.send({'name': 'City of Dorado', 'id': userId, 'demand_gph': waterLevel})    
    } catch (e) {
        res.status(500).end()
    }
})

app.listen(5003, () => console.log('User demand API listening on port 5003!'))
