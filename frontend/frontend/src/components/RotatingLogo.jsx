import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'

function TorusRings() {
  const outerRingRef = useRef()
  const innerRingRef = useRef()

  useFrame((state) => {
    if (outerRingRef.current && innerRingRef.current) {
      const time = state.clock.getElapsedTime()
      outerRingRef.current.rotation.x = time * 0.3
      outerRingRef.current.rotation.y = time * 0.2
      innerRingRef.current.rotation.x = -time * 0.2
      innerRingRef.current.rotation.y = time * 0.3
    }
  })

  return (
    <group>
      <mesh ref={outerRingRef}>
        <torusGeometry args={[3, 0.6, 32, 100]} />
        <meshStandardMaterial
          color="#8080ff"
          emissive="#4040ff"
          emissiveIntensity={0.5}
          roughness={0.1}
          metalness={0.8}
        />
      </mesh>

      <mesh ref={innerRingRef}>
        <torusGeometry args={[2.2, 0.5, 32, 100]} />
        <meshStandardMaterial
          color="#e0e0ff"
          emissive="#ffffff"
          emissiveIntensity={0.3}
          roughness={0.2}
          metalness={0.9}
        />
      </mesh>

      <mesh>
        <sphereGeometry args={[1.3, 64, 64]} />
        <meshStandardMaterial
          color="#1a1a2e"
          emissive="#0f0f1e"
          roughness={0.3}
          metalness={0.7}
        />
      </mesh>

      <mesh>
        <sphereGeometry args={[4, 32, 32]} />
        <meshBasicMaterial
          color="#6060ff"
          transparent={true}
          opacity={0.05}
        />
      </mesh>
    </group>
  )
}

function Scene() {
  return (
    <React.Fragment>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#8080ff" />
      <spotLight position={[0, 10, 0]} angle={0.3} penumbra={1} intensity={1} />
      <TorusRings />
      <OrbitControls
        enableZoom={false}
        enablePan={false}
        autoRotate={true}
        autoRotateSpeed={0.5}
        minPolarAngle={Math.PI / 3}
        maxPolarAngle={Math.PI / 1.5}
      />
    </React.Fragment>
  )
}

export default function RotatingLogo() {
  return (
    <div className="w-full h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <Canvas
        camera={{ position: [0, 0, 10], fov: 50 }}
        gl={{ antialias: true, alpha: true }}
      >
        <Scene />
      </Canvas>
    </div>
  )
}
