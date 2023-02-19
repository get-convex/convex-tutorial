import React, { useState, useEffect } from 'react';
import './Home.css';
import Container from 'react-bootstrap/Container';
import Card from 'react-bootstrap/Card';
import Image from 'react-bootstrap/Image';
import { Col, Row, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        // <Container>

        //     {/* <Image fluid width="75px" src='src/public/pexels-amina-filkins-5414051.jpg'></Image> */}
        //     <Container style={{ padding: "0.5rem" }}>
        //         <Row style={{}}>
        //             <h1 className='title'>nearbuy</h1>
        //             <Col sm="4">
        //                 <Image style={{ borderRadius: "25%", width: "30%", height: "80%" }} fluid roundedCircle src="src/public/pexels-amina-filkins-5414051.jpg" alt="Card image" />
        //                 {/*<Image style={{ paddingLeft: "2rem", borderRadius: "70%", width: "25%", position: "relative", top: "-8rem" }} fluid roundedCircle src="src/public/pexels-laura-james-6097827.jpg" alt="Card image" />*/}
        //             </Col>
        //             <Col sm="8">
        //                 <span style={{
        //                     paddingLeft: "2rem", position: "relative", top: "-28rem", fontWeight: 'light', fontSize: "3rem", letterSpacing: "0.25rem",
        //                 }}>
        //                     EXPLORE LOCAL MARKETS
        //                 </span>



        //             </Col>
        //         </Row>
        //     </Container>

        // </Container >
        <Container>
            <h1 className='title'>nearbuy</h1>
            <Row>
                <div style={{ display: "inline-block" }}>
                    <video style={{ opacity: "0.75" }} autoPlay loop className="background-vid">
                        <source src="src/public/mov.mp4" type="video/mp4" />
                    </video>
                </div>
                <p style={{ marginTop: "55vh", textAlign: "center", display: "block", fontSize: "1.5rem", fontWeight: "normal", letterSpacing: "0.25rem" }}> support small businesses nearby.</p>
                <p style={{ textAlign: "center", display: "block", fontSize: "1.5rem", fontWeight: "lighter", letterSpacing: "0.1rem" }}> login with your email today to begin your
                    search for local businesses in the area.</p>
                <div style={{ textAlign: "center", marginTop: "2rem" }}>
                    {/* <Button style={{ padding: "0.75rem 1.5rem 1rem 1.5rem", margin: "1.5rem", textAlign: "center", fontSize: "1.5rem", fontWeight: "normal" }}> get started &rarr;</Button> */}
                    <Link className="button" to="login">get started &rarr;</Link>
                </div>
            </Row>
        </Container>

    );

}

export default Home;