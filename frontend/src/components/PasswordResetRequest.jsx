import React, { useState } from 'react';
import { toast } from 'react-toastify';
import AxiosInstance from '../utils/AxiosInstance';

const PasswordResetRequest = () => {
    const [email, setEmail] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const validateEmail = (email) => {
        const re = /\S+@\S+\.\S+/;
        return re.test(email);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateEmail(email)) {
            toast.error("Please enter a valid email address");
            return;
        }

        setIsSubmitting(true);

        try {
            const res = await AxiosInstance.post('auth/password-reset/', { 'email': email });
            if (res.status === 200) {
                toast.success('A link to reset your password has been sent to your email');
                setEmail("");  // Clear the email field only on success
            }
        } catch (error) {
            toast.error("Failed to send reset link. Please try again later.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div>
            <h2>Enter your registered email</h2>
            <div className='wrapper'>
                <form onSubmit={handleSubmit}>
                    <div className='form-group'>
                        <label>Email Address:</label>
                        <input
                            type="text"
                            className='email-form'
                            name="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            disabled={isSubmitting}
                        />
                    </div>
                    <button className='vbtn' type="submit" disabled={isSubmitting}>
                        {isSubmitting ? "Sending..." : "Send"}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default PasswordResetRequest;
