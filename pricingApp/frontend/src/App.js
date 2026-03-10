import { useState } from 'react';
import Login from './components/Login';

function App() {
  const [user, setUser] = useState(null);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <Login user={user} onLogin={handleLogin} onLogout={handleLogout} />
  );
}

export default App;
