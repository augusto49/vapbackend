import React, { useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { toast } from 'react-toastify';
import AxiosInstance from '../utils/AxiosInstance';

const Profile = () => {
    const jwt = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user'));
    const navigate = useNavigate();

    useEffect(() => {
        if (!jwt || !user) {
            navigate('/login');
        } else {
            getSomeData();
        }
    }, [jwt, user, navigate]);

    const getSomeData = async () => {
        try {
            const res = await AxiosInstance.get('auth/profile/');
            console.log(res.data);
        } catch (error) {
            toast.error("Failed to fetch data");
            console.error(error);
        }
    };

    const refresh = JSON.parse(localStorage.getItem('refresh_token'));

    const handleLogout = async () => {
        try {
            const res = await AxiosInstance.post('auth/logout/', { 'refresh_token': refresh });
            if (res.status === 204) {
                toast.warn("Logout successful");
            }
        } catch (error) {
            toast.error("Logout failed, clearing session data");
            console.error(error);
        } finally {
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            navigate('/login');
        }
    };

    return (
        <div className='container'>
            <h2>Hi {user && user.full_name}</h2>
            <p style={{ textAlign: 'center' }}>Welcome to your profile</p>
            <button onClick={handleLogout} className='logout-btn'>Logout</button>
        </div>
    );
}

export default Profile;
