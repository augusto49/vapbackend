import React, { useState } from 'react';
import { useParams, useNavigate } from "react-router-dom";
import { toast } from 'react-toastify';
import AxiosInstance from '../utils/AxiosInstance';

const ResetPassword = () => {
  const navigate = useNavigate();
  const { uid, token } = useParams();
  const [newpasswords, setNewPassword] = useState({
    password: "",
    confirm_password: "",
  });
  const { password, confirm_password } = newpasswords;

  const handleChange = (e) => {
    setNewPassword({ ...newpasswords, [e.target.name]: e.target.value });
  }

  const data = {
    "password": password,
    "confirm_password": confirm_password,
    "uidb64": uid,
    "token": token,
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirm_password) {
      toast.error("Passwords do not match");
      return;
    }
    
    try {
      const res = await AxiosInstance.patch('auth/set-new-password/', data);
      if (res.status === 200) {
        toast.success(res.data.message);
        navigate('/login');
      }
    } catch (error) {
      toast.error("Something went wrong. Please try again.");
      console.error('Error resetting password:', error.response ? error.response.data : error.message);
    }
  }

  return (
    <div>
      <div className='form-container'>
        <div className='wrapper' style={{ width: "100%" }}>
          <h2>Enter your New Password</h2>
          <form onSubmit={handleSubmit}>
            <div className='form-group'>
              <label htmlFor="password">New Password:</label>
              <input 
                type="password"
                className='email-form'
                name="password"
                value={password}
                onChange={handleChange}
                required
              />
            </div>
            <div className='form-group'>
              <label htmlFor="confirm_password">Confirm Password</label>
              <input 
                type="password"
                className='email-form'
                name="confirm_password"
                value={confirm_password}
                onChange={handleChange}
                required
              />
            </div>
            <button type='submit' className='vbtn'>Submit</button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ResetPassword;
