import { AuthProvider } from './contexts/AuthContext'
import { AuthDemo } from './components/AuthDemo'

function App() {
  return (
    <AuthProvider>
      <AuthDemo />
    </AuthProvider>
  )
}

export default App
