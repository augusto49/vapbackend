const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Quando um cliente se conecta
io.on('connection', (socket) => {
    console.log('Novo cliente conectado: ', socket.id);

    // Evento de nova corrida
    socket.on('newRideRequest', (rideData) => {
        console.log('Nova corrida recebida: ', rideData);

        // Enviar para todos os motoristas online
        io.emit('rideRequest', {
            start_location: rideData.start_location,
            end_location: rideData.end_location,
            distance: rideData.distance,
            price: rideData.price,
            user_id: rideData.user_id
        });
    });

    // Evento de aceitação de corrida
    socket.on('rideAccepted', (rideData) => {
        console.log('Corrida aceita: ', rideData);

        // Enviar a atualização para todos os clientes
        io.emit('rideAccepted', {
            ride_id: rideData.ride_id,
            driver_id: rideData.driver_id,
            status: rideData.status
        });
    });

    // Evento de cancelamento de corrida
    socket.on('rideCancelled', (rideData) => {
        console.log('Corrida cancelada: ', rideData);

        // Enviar a atualização para todos os clientes
        io.emit('rideCancelled', {
            ride_id: rideData.ride_id,
            status: rideData.status,
            canceled_by: rideData.canceled_by
        });
    });

    // Evento de atualização da localização do motorista
    socket.on('updateDriverLocation', (locationData) => {
        console.log('Atualização de localização do motorista: ', locationData);

        // Enviar a atualização para todos os clientes
        io.emit('driverLocationUpdated', {
            user_id: locationData.user_id,
            latitude: locationData.latitude,
            longitude: locationData.longitude
        });
    });

    socket.on('disconnect', () => {
        console.log('Cliente desconectado: ', socket.id);
    });
});

server.listen(3000, () => {
    console.log('Servidor WebSocket rodando na porta 3000');
});
