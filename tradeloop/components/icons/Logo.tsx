const Logo = ({ className = '', ...props }) => (
  <img
    src="/LoopH.png" // Use the path to the logo.svg file in the public directory
    alt="Logo"
    width={32} // 32 by default
    height={32} // 32 by default
    className={className}
    {...props}
  />
);

export default Logo;
