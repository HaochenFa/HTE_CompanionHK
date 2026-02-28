import { createTheme } from "@mui/material/styles";

export const companionTheme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#5A67D8",
    },
    secondary: {
      main: "#ED64A6",
    },
    background: {
      default: "#F7FAFC",
    },
  },
  shape: {
    borderRadius: 12,
  },
});
