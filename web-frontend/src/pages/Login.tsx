import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Input, Card, CardBody, CardHeader, Divider } from "@heroui/react";
import { loginUser } from "../api/auth";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await loginUser(username, password);
      navigate("/dashboard");
    } catch (error) {
      console.error("Login failed", error);
      alert("Login failed! Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
      <Card className="w-full max-w-md p-4">
        <CardHeader className="flex flex-col gap-1 items-start">
          <h1 className="text-2xl font-bold">Welcome Back</h1>
          <p className="text-small text-default-500">Log in to access your diagrams</p>
        </CardHeader>

        <Divider className="my-2" />

        <CardBody>
          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <Input
              isRequired
              label="Username"
              placeholder="Enter your username"
              type="text"
              variant="bordered"
              value={username}
              onValueChange={setUsername}
            />
            <Input
              isRequired
              label="Password"
              placeholder="Enter your password"
              type="password"
              variant="bordered"
              value={password}
              onValueChange={setPassword}
            />

            <div className="flex justify-end">
              <Link to="#" className="text-xs text-primary hover:underline">
                Forgot password?
              </Link>
            </div>

            <Button color="primary" type="submit" className="w-full font-semibold" isLoading={isLoading}>
              Sign In
            </Button>
          </form>

          <div className="mt-4 text-center text-sm">
            <p className="text-gray-500">
              Don't have an account?{" "}
              <Link to="/register" className="text-primary font-bold hover:underline">
                Sign Up
              </Link>
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}