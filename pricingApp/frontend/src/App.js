import { useState } from 'react';
import Login from './components/Login';
import ProductList from './components/ProductList';

function App() {
  const [user, setUser] = useState(null);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (!user) {
    return (
      <Login user={user} onLogin={handleLogin} onLogout={handleLogout} />
    );
  }

  return <ProductList />;
}

export default App;
