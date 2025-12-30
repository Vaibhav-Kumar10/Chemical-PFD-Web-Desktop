import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Input, Card, CardBody, CardHeader, Divider } from "@heroui/react";
import { registerUser } from "../api/auth";

export default function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: ""
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    setIsLoading(true);
    try {
      // Map 'username' field to backend expected 'username'
      await registerUser(formData.username, formData.email, formData.password);
      alert("Registration successful! Please login.");
      navigate("/login");
    } catch (error) {
      console.error("Registration error", error);
      alert("Registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
      <Card className="w-full max-w-md p-4">
        <CardHeader className="flex flex-col gap-1 items-start">
          <h1 className="text-2xl font-bold">Create Account</h1>
          <p className="text-small text-default-500">Join the Chemical PFD Builder team</p>
        </CardHeader>

        <Divider className="my-2" />

        <CardBody>
          <form onSubmit={handleRegister} className="flex flex-col gap-4">
            <Input
              isRequired
              label="Username"
              placeholder="Choose a username"
              variant="bordered"
              value={formData.username}
              onValueChange={(v) => handleChange("username", v)}
            />
            <Input
              isRequired
              label="Email"
              placeholder="Enter your email"
              type="email"
              variant="bordered"
              value={formData.email}
              onValueChange={(v) => handleChange("email", v)}
            />
            <Input
              isRequired
              label="Password"
              placeholder="Create a password"
              type="password"
              variant="bordered"
              value={formData.password}
              onValueChange={(v) => handleChange("password", v)}
            />
            <Input
              isRequired
              label="Confirm Password"
              placeholder="Confirm your password"
              type="password"
              variant="bordered"
              value={formData.confirmPassword}
              onValueChange={(v) => handleChange("confirmPassword", v)}
            />

            <Button color="success" type="submit" className="w-full font-semibold text-white" isLoading={isLoading}>
              Sign Up
            </Button>
          </form>

          <div className="mt-4 text-center text-sm">
            <p className="text-gray-500">
              Already have an account?{" "}
              <Link to="/login" className="text-primary font-bold hover:underline">
                Log In
              </Link>
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}