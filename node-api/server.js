const tracer = require('dd-trace').init({hostname:'agent'})
const express = require('express')
const redis = require('redis')
const {promisify} = require('util')

const client = redis.createClient(6379, 'redis')

client.on('connect', () => {
    console.log('Redis client connected');
})

client.on('error', (err) => {
    console.log('Couldn\'t connect to redis: ' + err)
})

const existsAsync = promisify(client.exists).bind(client)
const hgetallAsync = promisify(client.hgetall).bind(client)
const hmsetAsync = promisify(client.hmset).bind(client)

const users = [{'name': 'City of Dorondo', 'uid': '123e4567-e89b-12d3-a456-426655440000', 'demand_gph': 110},
                {'name': 'Cortland County', 'uid': '223e4567-e89b-12d3-a456-625655440000', 'demand_gph': 210},
                {'name': 'C3 Energy', 'uid': '333e4567-c89b-12d3-a456-785655440000', 'demand_gph': 5000}]

async function addUsers() {
    for (var user of users) {
        // only write user ids if users don't exist
        const exists = await existsAsync(user.uid)
        if (exists == 1) {
            console.log('skipping ' + user.uid + ' as it exists')
        }
        else {
            console.log('creating ' + user.uid)
            const created = await hmsetAsync(user.uid, {
                'name': user.name,
                'demand_gph': user.demand_gph
            }) 
            console.log(created)
        }
    }
}

addUsers()

const app = express()

app.get('/', (req, res) => {
    res.send({'Hello from Water Usage': 'World!'})
})

app.get('/users', async (req, res) => {
    await res.send(users)
})

app.get('/users-alt', (req, res) => {
    res.send(users)
})

app.post('/users/:userId/:waterLevel(\\d+)', async (req, res) => {
    try {
        const waterLevel = parseInt(req.params.waterLevel)
        const userId = req.params.userId
        await res.send({'name': 'City of Dorado', 'id': userId, 'demand_gph': waterLevel})    
    } catch (e) {
        res.status(500).end()
    }
})

app.listen(5003, () => console.log('User demand API listening on port 5003!'))
