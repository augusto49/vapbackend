import React, { useEffect, useState } from 'react';
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const Signup = () => {
    const navigate = useNavigate();
    const [formdata, setFormdata] = useState({
        email: "",
        first_name: "",
        last_name: "",
        password: "",
        password2: ""
    });

    const [error, setError] = useState('');

    const handleOnchange = (e) => {
        setFormdata({ ...formdata, [e.target.name]: e.target.value });
    };

    const handleSigninWithGoogle = async (response) => {
        try {
            const payload = response.credential;
            const server_res = await axios.post("http://127.0.0.1:8000/api/v1/auth/google/", { 'access_token': payload });
            console.log(server_res.data);
            toast.success("Google signup successful!");
            navigate("/dashboard");
        } catch (error) {
            toast.error("Google signup failed: " + (error.response?.data?.message || error.message));
        }
    };

    useEffect(() => {
        /* global google */
        google.accounts.id.initialize({
            client_id: import.meta.env.VITE_CLIENT_ID,
            callback: handleSigninWithGoogle
        });
        google.accounts.id.renderButton(
            document.getElementById("signInDiv"),
            { theme: "outline", size: "large", text: "continue_with", shape: "circle", width: "280" }
        );
    }, []);

    const { email, first_name, last_name, password, password2 } = formdata;

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (password !== password2) {
            setError("Passwords do not match");
            toast.error("Passwords do not match");
            return;
        }

        try {
            const response = await axios.post('http://127.0.0.1:8000/api/v1/auth/register/', formdata);
            const result = response.data;

            if (response.status === 201) {
                toast.success(result.message);
                navigate("/otp/verify");
            } else {
                toast.error("Signup failed");
            }
        } catch (error) {
            toast.error("Signup failed: " + (error.response?.data?.message || error.message));
        }
    };

    return (
        <div>
            <div className='form-container'>
                <div style={{ width: "100%" }} className='wrapper'>
                    <h2>Create Account</h2>
                    <form onSubmit={handleSubmit}>
                        <div className='form-group'>
                            <label>Email Address:</label>
                            <input type="text"
                                className='email-form'
                                name="email"
                                value={email}
                                onChange={handleOnchange}
                            />
                        </div>
                        <div className='form-group'>
                            <label>First Name:</label>
                            <input type="text"
                                className='email-form'
                                name="first_name"
                                value={first_name}
                                onChange={handleOnchange}
                            />
                        </div>
                        <div className='form-group'>
                            <label>Last Name:</label>
                            <input type="text"
                                className='email-form'
                                name="last_name"
                                value={last_name}
                                onChange={handleOnchange}
                            />
                        </div>
                        <div className='form-group'>
                            <label>Password:</label>
                            <input type="password"
                                className='email-form'
                                name="password"
                                value={password}
                                onChange={handleOnchange}
                            />
                        </div>
                        <div className='form-group'>
                            <label>Confirm Password:</label>
                            <input type="password"
                                className='email-form'
                                name="password2"
                                value={password2}
                                onChange={handleOnchange}
                            />
                        </div>
                        {error && <p className='error'>{error}</p>}
                        <input type="submit" value="Submit" className="submitButton" />
                    </form>
                    <h3 className='text-option'>Or</h3>
                    <div className='googleContainer'>
                        <div id="signInDiv" className='gsignIn'></div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Signup;
