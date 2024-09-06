import axios from "axios";
import dayjs from "dayjs";

let accessToken = localStorage.getItem('token') ? JSON.parse(localStorage.getItem('token')) : "";
let refreshToken = localStorage.getItem('refresh_token') ? JSON.parse(localStorage.getItem('refresh_token')) : "";

const baseURL = 'http://192.168.3.74:8000/api/v1/';

const AxiosInstance = axios.create({
    baseURL: baseURL,
    headers: {
        'Content-Type': 'application/json',
        Authorization: accessToken ? `Bearer ${accessToken}` : ""
    },
});

AxiosInstance.interceptors.request.use(async req => {
    if (accessToken) {
        const user = jwt_decode(accessToken);
        const isExpired = dayjs.unix(user.exp).diff(dayjs()) < 1;

        if (!isExpired) {
            req.headers.Authorization = `Bearer ${accessToken}`;
            return req;
        }

        try {
            const response = await axios.post(`${baseURL}auth/token/refresh/`, {
                refresh: refreshToken
            });

            accessToken = response.data.access;
            localStorage.setItem('token', JSON.stringify(accessToken));

            req.headers.Authorization = `Bearer ${accessToken}`;
        } catch (error) {
            console.error('Error refreshing token:', error);
            // Trate o erro, como redirecionar para a página de login ou exibir uma mensagem de erro
        }
    } else {
        req.headers.Authorization = localStorage.getItem('token') ? `Bearer ${JSON.parse(localStorage.getItem('token'))}` : "";
    }

    return req;
}, error => {
    return Promise.reject(error);
});

export default AxiosInstance;
