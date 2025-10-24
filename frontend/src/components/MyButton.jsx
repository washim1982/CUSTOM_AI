// frontend/src/components/MyButton.jsx
import React from 'react';
import Button from '@mui/material/Button'; // Import the component from the library

function MyButton({ label }) {
  return (
    <Button variant="contained" color="primary">
      {label}
    </Button>
  );
}

export default MyButton;
