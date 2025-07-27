import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { LogOut } from 'lucide-react';

export const AuthDemo: React.FC = () => {
  const [showLogin, setShowLogin] = useState(true);
  const { user, logout } = useAuth();

  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Welcome back!</CardTitle>
            <CardDescription>You are successfully logged in</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-sm text-muted-foreground">
              Logged in as: <span className="font-medium text-foreground">{user.email}</span>
            </div>
            <Button onClick={logout} variant="outline" className="w-full">
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      <div className="w-full max-w-md space-y-4">
        <div className="flex justify-center space-x-2 mb-4">
          <Button
            variant={showLogin ? "default" : "outline"}
            onClick={() => setShowLogin(true)}
          >
            Login
          </Button>
          <Button
            variant={!showLogin ? "default" : "outline"}
            onClick={() => setShowLogin(false)}
          >
            Register
          </Button>
        </div>
        {showLogin ? <LoginForm /> : <RegisterForm />}
      </div>
    </div>
  );
};