import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { toast } from 'react-toastify';
import AxiosInstance from "../utils/AxiosInstance";

const Login = () => {
    const navigate = useNavigate();
    const [searchparams] = useSearchParams();
    const [logindata, setLogindata] = useState({
        email: "",
        password: ""
    });

    const handleOnchange = (e) => {
        setLogindata({ ...logindata, [e.target.name]: e.target.value });
    };

    const handleLoginWithGoogle = (response) => {
        console.log("id_token", response.credential);
    };

    useEffect(() => {
        /* global google */
        google.accounts.id.initialize({
            client_id: import.meta.env.VITE_CLIENT_ID,
            callback: handleLoginWithGoogle
        });
        google.accounts.id.renderButton(
            document.getElementById("signInDiv"),
            { theme: "outline", size: "large", text: "continue_with", shape: "circle", width: "280" }
        );
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await AxiosInstance.post('auth/login/', logindata);
            const response = res.data;
            if (res.status === 200) {
                const user = {
                    'full_name': response.full_name,
                    'email': response.email
                };
                localStorage.setItem('token', JSON.stringify(response.access_token));
                localStorage.setItem('refresh_token', JSON.stringify(response.refresh_token));
                localStorage.setItem('user', JSON.stringify(user));
                await navigate('/dashboard');
                toast.success('Login successful');
            } else {
                toast.error('Something went wrong');
            }
        } catch (error) {
            toast.error('Login failed: ' + (error.response?.data?.message || error.message));
        }
    };

    return (
        <div>
            <div className='form-container'>
                <div style={{ width: "100%" }} className='wrapper'>
                    <h2>Login into your account</h2>
                    <form onSubmit={handleSubmit}>
                        <div className='form-group'>
                            <label>Email Address:</label>
                            <input type="text"
                                   className='email-form'
                                   value={logindata.email}
                                   name="email"
                                   onChange={handleOnchange}
                            />
                        </div>
                        <div className='form-group'>
                            <label>Password:</label>
                            <input type="password"
                                   className='email-form'
                                   value={logindata.password}
                                   name="password"
                                   onChange={handleOnchange}
                            />
                        </div>
                        <input type="submit" value="Login" className="submitButton" />
                        <p className='pass-link'><Link to={'/forget-password'}>Forgot password?</Link></p>
                    </form>
                    <h3 className='text-option'>Or</h3>
                    <div id="signInDiv"></div>
                </div>
            </div>
        </div>
    );
};

export default Login;
