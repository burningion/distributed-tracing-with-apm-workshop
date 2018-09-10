const tracer = require('dd-trace').init({hostname:'agent'})
const express = require('express')
const app = express()

app.get('/', (req, res) => {
    res.send({'hello': 'world'})
})

app.get('/users', async (req, res) => {
    await res.send({'users': [{'name': 'City of Dorondo', 'id': 1, 'demand_gph': 100},
                    {'name': 'Cortland County', 'id': 2, 'demand_gph': 200},
                    {'name': 'C3 Energy', 'id': 3, 'demand_gph': 4000}]})
})

app.get('/users-alt', (req, res) => {
    res.send({'users': [{'name': 'City of Dorondo', 'id': 1, 'demand_gph': 100},
                        {'name': 'Cortland County', 'id': 2, 'demand_gph': 200},
                        {'name': 'C3 Energy', 'id': 3, 'demand_gph': 4000}]})
})

app.listen(5003, () => console.log('User demand API listening on port 5003!'))
