

import { useEffect, useState } from 'react';

function useAuth() {
  const [logged, setLogged] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    fetch('/api/login')
      .then((res) => res.json())
      .then((data) => {
        if (data?.user) {
          setLogged(true);
          setIsAdmin(data.user.role === 'admin');
        } else {
          setLogged(false);
          setIsAdmin(false);
        }
      })
      .catch((err) => {
        console.error('Error fetching login:', err);
        setLogged(false);
        setIsAdmin(false);
      });
  }, []);

  return { logged, isAdmin };
}

export default useAuth;